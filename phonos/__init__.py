from flask import Flask
from phonos import settings

import os

config_path = os.environ.get("PHONOS_CONFIG", f"{os.getcwd()}/phonos.cfg")

app = Flask(__name__)
app.config.from_mapping(settings.DEFAULTS)
app.config.from_pyfile(config_path)

@app.route('/')
def hello():
    return "Hi there!"
