from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
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

def test_job():
    print("The job ran!")

scheduler = BackgroundScheduler(
    jobstores={'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])}
)
scheduler.start()
#scheduler.add_job(test_job, trigger='cron', timezone="UTC")

from phonos.ui_routes import *
