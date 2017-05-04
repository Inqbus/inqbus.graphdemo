import os
from logging import getLogger

import subprocess

import atexit

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_menu import Menu
from inqbus.graphdemo.config.config import configure_app
from inqbus.graphdemo.constants import FLASK_HOST, BOKEH_HOST
from inqbus.graphdemo.database.functions import set_up_db
from inqbus.graphdemo.database.model import DB
from inqbus.graphdemo.routing.routes import set_up_routes


def set_up_file_storage(app):
    directory = app.config['UPLOAD_FOLDER']

    if not os.path.exists(directory):
        os.makedirs(directory)


application = Flask(__name__)


Menu(app=application)
Bootstrap(application)

configure_app(application)
set_up_db(application)
set_up_routes(application)
set_up_file_storage(application)


@application.teardown_appcontext
def shutdown_session(exception=None):
    DB.session.close()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(dir_path, 'sliders.py')

    # using the bokeh socket does not work properly
    # bokeh_process = subprocess.Popen(
    #     ['bokeh', 'serve','--allow-websocket-origin=%s' % FLASK_HOST,
    #      '--allow-websocket-origin=%s' % BOKEH_HOST, file], stdout=subprocess.PIPE)

    # @atexit.register
    # def kill_server():
    #     bokeh_process.kill()

    application.run(host="0.0.0.0")
