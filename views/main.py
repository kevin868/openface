"""
Views to interact with flask server
"""
from flask import Blueprint, jsonify, request, make_response

MAIN_BLUEPRINT = Blueprint("main", __name__)


@MAIN_BLUEPRINT.route("/health", methods=["GET"])
def get_health():
    """
    Check health of the service

    Returns:
        Health status of the service
    """
    print 'health'
    return "OK"


@MAIN_BLUEPRINT.route("/post_imgs", methods=["POST", "OPTIONS"])
def post_images():
    print('post_imgs')
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "POST": # The actual request following the preflight
        output = {"msg": "Rokay"}
        return _corsify_actual_response(output)
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))
    print('finished')

def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(output):
    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response