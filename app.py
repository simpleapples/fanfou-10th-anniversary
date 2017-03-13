# coding: utf-8

from flask import Flask
from flask_login import LoginManager
from leancloud import Object
from leancloud import LeanCloudError
from views.auth import auth_view
from views.main import main_view
import const


def init_app(app):
    app.config.update({'SECRET_KEY': const.SECRET_KEY})

    login_manager = LoginManager(app)
    login_manager.session_protection = 'basic'
    login_manager.login_view = 'auth.xauth'
    login_manager.refresh_view = 'auth.xauth'

    class FFAuth(Object):
        pass

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return FFAuth.query.get(user_id)
        except LeanCloudError as _:
            pass
        return None

    app.register_blueprint(main_view)
    app.register_blueprint(auth_view)

app = Flask(__name__)
init_app(app)
