"""
Main entry point for running the service, through command line or mod_wsgi.
"""
from os import getenv

from flask import Flask, jsonify
from views.main import MAIN_BLUEPRINT


application = Flask(__name__)

def construct_error_json(error_code, message):
    response = jsonify({"error": message})
    response.status_code = error_code
    return response


# @application.errorhandler(HTTPStatus.BAD_REQUEST)  # 400
# @application.errorhandler(HTTPStatus.UNAUTHORIZED)  # 401
# @application.errorhandler(HTTPStatus.FORBIDDEN)  # 403
# @application.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)  # 500
# def bad_request_handler(error):
#     """This exception handler is used to respond via JSON
#     rather than a regular HTML encoded exception"""
#     print(error)
#     return construct_error_json(error.code, error.description)


def destroy():
    """
    Shutdown the service gracefully, cleaning up resources created in init().
    """
    print("Stopping server")


if __name__ == "__main__":
    """
    Called as main python script, start the server.
    """
    application.debug = True

    # Start the flask server, this runs until ctrl-c is pressed.
    #
    # `entire_network` will run your service in a way that will allow all devices
    # on the same network to connect to it. This is unsafe in particular if you
    # set debug=True, because any user of the application can execute arbitrary
    # Python code on your computer. If you trust the users on the network,
    # you can set this and access the app from, say, your phone.
    only_on_localhost = "localhost"
    on_entire_network = "0.0.0.0"

    print("Serving on: http://localhost:8089")
    application.register_blueprint(MAIN_BLUEPRINT)
    application.run(on_entire_network, 8089)

    destroy()

elif __name__.startswith(("_mod_wsgi_", "uwsgi_file_application")):
    # Called from apache httpd mod_wsgi or uwsgi on start, initialize the server.
    pass
