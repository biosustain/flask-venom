from flask import json, Flask
from flask.testing import FlaskClient
from flask_testing import TestCase as TestCase_


class JSONClient(FlaskClient):
    def open(self, *args, **kwargs):
        headers = kwargs.pop('headers', [])
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
            kwargs['content_type'] = 'application/json'
        return super().open(*args, headers=headers, **kwargs)


class TestCase(TestCase_):
    def create_app(self):
        app = Flask(__name__)
        app.test_client_class = JSONClient
        app.debug = True
        return app
