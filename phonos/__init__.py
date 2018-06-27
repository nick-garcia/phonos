from flask import Flask
from flask_login import LoginManager
from phonos import settings

import os

config_path = os.environ.get("PHONOS_CONFIG", f"{os.getcwd()}/phonos.cfg")

app = Flask(__name__)
app.config.from_mapping(settings.DEFAULTS)
app.config.from_pyfile(config_path)

login = LoginManager(app)
login.login_view = 'login_html'

from phonos.ui_routes import *
