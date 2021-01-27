from app import application
from views.main import MAIN_BLUEPRINT

# This file is an entrypoint for gunicorn

@MAIN_BLUEPRINT.route("/.well-known/pki-validation/8F5A6974D3B23438ADA99F22F9E508E3.txt", methods=["GET"])
def get_cert_verification():
    """

    Returns:
        Text file from sslforfree.com
    """
    print('cert')
    return application.send_static_file('8F5A6974D3B23438ADA99F22F9E508E3.txt')

application.register_blueprint(MAIN_BLUEPRINT)

if __name__ == "__main__":
    application.run()
