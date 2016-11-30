from typing import Optional, Union, Type

import flask
import venom.rpc


def route_view(venom: 'venom.rpc.Venom',
               service: Type['venom.rpc.Service'],
               rpc: Method,
               wire_format: Type[WireFormat]):


# TODO a generic REST interface for both aiohttp and flask.
def http_view_factory(rpc: venom.rpc.method.Method):
    # TODO how to resolve url parameters
    # TODO how to resolve request body
    # TODO how to format response (body, content_type, status) -- return tuple?

    # view(query, text/data)

    #return _make_response(data, code, headers)
    pass


class Venom(venom.rpc.Venom):
    def __init__(self, app=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app  # type: Optional[flask.Flask]
        self.blueprint = None  # type: flask.Blueprint
        self.views = []

    def init_app(self, app: Union[flask.Flask, flask.Blueprint]):
        # if app is a blueprint, defer the initialization
        if isinstance(app, flask.Blueprint):
            app.record(self._deferred_blueprint_init)
            self.blueprint = app
        else:
            self._init_app(app)

    def _deferred_blueprint_init(self, setup_state: 'flask.blueprints.BlueprintSetupState'):
        self._init_app(setup_state.app, url_prefix=setup_state.url_prefix)

    def _init_app(self, app: flask.Flask, url_prefix: str = None):
        """
        :param app: a :class:`Flask` instance
        """
        # app.config.setdefault('POTION_MAX_PER_PAGE', 100)
        # app.config.setdefault('POTION_DEFAULT_PER_PAGE', 20)

        for route, resource, view_func, endpoint, methods in self.views:
            rule = route.rule_factory(resource)
            if self.blueprint:
                endpoint = '{}.{}'.format(self.blueprint.name, endpoint)

            app.add_url_rule(rule,
                             view_func=view_func,
                             endpoint=endpoint,
                             methods=methods)

            # app.handle_exception = partial(self._exception_handler, app.handle_exception)
            # app.handle_user_exception = partial(self._exception_handler, app.handle_user_exception)

    def _add_method_url_rule(self, service: Type[Service], rpc: 'venom.rpc.method.Method'):
        if self.app:
            self.app.add_url_rule(rule, view_func=view, endpoint=endpoint, methods=methods)
        else:
            self.views.append((route, resource, view, endpoint, methods))

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
