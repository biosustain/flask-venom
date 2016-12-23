import asyncio
from typing import Union, Type

import flask
import venom.rpc
from venom.exceptions import ErrorResponse, Error
from venom.rpc.method import HTTPVerb, HTTPFieldLocation
from venom.serialization import WireFormat, JSON, string_decoder
from .utils import uri_pattern_to_uri_rule


def http_view_factory(venom: 'venom.rpc.Venom',
                      service: Type['venom.rpc.service.Service'],
                      rpc: venom.rpc.method.Method,
                      wire_format: Type[WireFormat],
                      loop: 'asyncio.BaseEventLoop' = None):
    rpc_request = wire_format(rpc.request)
    rpc_response = wire_format(rpc.response)
    rpc_error_response = wire_format(ErrorResponse)

    http_status = rpc.http_status

    http_field_locations = rpc.http_field_locations()
    http_request_body = http_field_locations[HTTPFieldLocation.BODY]
    http_request_query = [(name, string_decoder(rpc.request.__fields__[name], wire_format))
                          for name in http_field_locations[HTTPFieldLocation.QUERY]]

    http_request_path = [(name, string_decoder(rpc.request.__fields__[name], wire_format))
                         for name in http_field_locations[HTTPFieldLocation.PATH]]

    if loop is None:
        loop = asyncio.get_event_loop()

    def view(**kwargs):
        try:
            if http_request_body:
                request = rpc_request.unpack(flask.request.get_data(), include=http_request_body)
            else:
                request = rpc.request()
                for name, decode in http_request_query:
                    try:
                        request[name] = decode(flask.request.args[name])
                    except KeyError:
                        pass

                rpc_request.decode(flask.request.args, include=http_request_query)

            for name, decode in http_request_path:
                try:
                    request[name] = decode(kwargs[name])
                except KeyError:
                    pass

            instance = venom.get_instance(service)
            response = loop.run_until_complete(rpc.invoke(instance, request, loop=loop))
            return flask.Response(rpc_response.pack(response),
                                  mimetype=rpc_error_response.mime,
                                  status=http_status)
        except Error as e:
            return flask.Response(rpc_error_response.pack(e.format()),
                                  mimetype=rpc_error_response.mime,
                                  status=e.http_status)

    return view


class Venom(venom.rpc.Venom):
    def __init__(self, app: flask.Flask = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.blueprint = None  # type: flask.Blueprint
        self.views = []

    def init_app(self, app: Union[flask.Flask, flask.Blueprint]):
        # if app is a blueprint, defer the initialization
        if isinstance(app, flask.Blueprint):
            app.record(self._deferred_blueprint_init)
            self.blueprint = app
        else:
            self._init_app(app)
            self.app = app

    def _deferred_blueprint_init(self, setup_state: 'flask.blueprints.BlueprintSetupState'):
        self._init_app(setup_state.app, url_prefix=setup_state.url_prefix)

    def _init_app(self, app: flask.Flask, url_prefix: str = None):
        for rule, view, endpoint, methods in self.views:
            if url_prefix:
                rule = url_prefix + rule

            if self.blueprint:
                endpoint = '{}.{}'.format(self.blueprint.name, endpoint)

            app.add_url_rule(rule, view_func=view, endpoint=endpoint, methods=methods)

    def _add_method_url_rule(self, service: Type['venom.rpc.service.Service'], rpc: 'venom.rpc.method.Method'):
        rule = uri_pattern_to_uri_rule(rpc.http_rule(service))
        view = http_view_factory(self, service, rpc, wire_format=JSON)
        methods = [rpc.http_verb.value]
        endpoint = '.'.join((service.__meta__.name, rpc.name))

        if self.app:
            self.app.add_url_rule(rule, view_func=view, endpoint=endpoint, methods=methods)
        else:
            self.views.append((rule, view, endpoint, methods))

    def add(self,
            service: Type['venom.rpc.service.Service'],
            client: Type['venom.rpc.comms.Client'] = None,
            *client_args,
            **client_kwargs) -> None:
        super().add(service, client, *client_args, **client_kwargs)

        if isinstance(service, venom.rpc.Stub):
            return

        for rpc in service.__methods__.values():
            self._add_method_url_rule(service, rpc)
