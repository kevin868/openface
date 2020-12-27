"""
Views to interact with flask server
"""
from flask import Blueprint, jsonify

MAIN_BLUEPRINT = Blueprint("main", __name__)


@MAIN_BLUEPRINT.route("/health", methods=["GET"])
def get_health():
    """
    Check health of the service

    Returns:
        Health status of the service
    """
    return "OK"


@MAIN_BLUEPRINT.route("/post_imgs", methods=["POST"])
def post_images():
    return "Rokay"