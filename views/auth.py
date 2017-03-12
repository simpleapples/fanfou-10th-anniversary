# coding: utf-8

from leancloud import LeanCloudError
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
import fanfou
import urllib
import json
from forms.auth import AuthForm
from models import FFAuth
import const


auth_view = Blueprint('auth', __name__)


@auth_view.route('/auth', methods=['GET', 'POST'])
def xauth():
    form = AuthForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            consumer = {'key': const.CONSUMER_KEY,
                        'secret': const.CONSUMER_SECRET}
            client = fanfou.XAuth(consumer, email, password)
            user_info = client.request('/users/show', 'POST')
            nickname = json.loads(user_info.read().decode('utf8'))['screen_name']
            try:
                ff_auth = FFAuth.query.equal_to('email', email).first()
            except LeanCloudError as err:
                if err.code == 101:
                    ff_auth = FFAuth()
            token = client.oauth_token['key'].decode('utf-8')
            secret = client.oauth_token['secret'].decode('utf-8')
            ff_auth.set('email', email)
            ff_auth.set('nickname', nickname)
            ff_auth.set('token', token)
            ff_auth.set('secret', secret)
            ff_auth.save()
            login_user(ff_auth, True)
            return redirect(url_for('main.index'))
        except LeanCloudError as _:
            error = '写入数据库失败'
        except urllib.error.HTTPError as _:
            error = '认证失败, 请输入正确的用户名和密码'
    else:
        error = '表单非法'
    return render_template('auth.html',
                           form=form,
                           error=error)


@auth_view.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
