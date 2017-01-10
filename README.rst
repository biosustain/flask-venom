===========
Flask-Venom
===========

A Flask extension for `Venom RPC <https://github.com/biosustain/venom>`_

This extension currently supports synchronous request/reply only.


::

    from flask import Flask
    from flask_venom import Venom
    from venom.rpc import Service
    from venom.rpc import http

    app = Flask(__name__)

    class HelloService(Service):
        @http('GET')
        def say_hello(self) -> str:
            return 'Hello!'

    venom.add(HelloService)
    venom = Venom(app)

    if __name__ == "__main__":
        app.run()
