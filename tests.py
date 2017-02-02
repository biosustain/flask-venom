from venom import Message
from venom.fields import String, Bool, Integer
from venom.rpc import Service, http

from flask_venom.test_utils import TestCase
from flask_venom import Venom


class FlaskVenomTestCase(TestCase):
    def test_get_request(self):
        venom = Venom(self.app)

        class GreetingRequest(Message):
            shout = Integer()  # TODO change to Bool(); requires string_decoder() support

        class HelloService(Service):
            @http.GET(request=GreetingRequest)
            def greeting(self, shout: int) -> str:
                return 'HI' if shout != 0 else 'Hi'

        venom.add(HelloService)

        response = self.client.get("/hello/greeting")
        self.assert200(response)
        self.assertEqual(response.json, 'Hi')

        response = self.client.get("/hello/greeting?shout=1")
        self.assert200(response)
        self.assertEqual(response.json, 'HI')

    def test_post_request(self):
        venom = Venom(self.app)

        class HelloRequest(Message):
            name = String()
            shout = Bool()

        class HelloResponse(Message):
            message = String()

        class HelloService(Service):
            @http.POST('./greet/{name}')
            def say_hello(self, request: HelloRequest) -> HelloResponse:
                text = "Hello, {}!".format(request.name)

                if request.shout:
                    text = text.upper()

                return HelloResponse(text)

        venom.add(HelloService)

        response = self.client.post("/hello/greet/Person", data={})
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'Hello, Person!'})

        response = self.client.post("/hello/greet/Person", data={'shout': True})
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'HELLO, PERSON!'})

    def test_exception(self):
        venom = Venom(self.app)

        class HelloService(Service):
            @http.GET
            def goodbye(self):
                raise NotImplementedError

        venom.add(HelloService)

        response = self.client.get("/hello/goodbye")
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.json, {'description': 'Not Implemented', 'status': 501})
