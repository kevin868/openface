from app import application
from views.main import MAIN_BLUEPRINT

# This file is an entrypoint for gunicorn

application.register_blueprint(MAIN_BLUEPRINT)

if __name__ == "__main__":
    application.run()
