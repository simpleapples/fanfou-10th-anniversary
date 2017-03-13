# coding: utf-8

from leancloud import LeanCloudError
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for, session, request
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
import fanfou
import urllib
import json
from forms.auth import AuthForm
from models import FFAuth
import const
from . import main
from requests_oauthlib import OAuth1Session, oauth1_session


auth_view = Blueprint('auth', __name__)


@auth_view.route('/xauth', methods=['GET', 'POST'])
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
        except urllib.error.HTTPError as err:
            error = '认证失败, 请输入正确的用户名和密码'
    else:
        error = '表单非法'
    return render_template('auth.html',
                           form=form,
                           error=error)


@auth_view.route('/oauth')
def oauth_request():
    try:
        o = OAuth1Session(const.CONSUMER_KEY, const.CONSUMER_SECRET)
        req = o.fetch_request_token("http://fanfou.com/oauth/request_token")

        ov = request.url_root[:-1] + url_for(".oauth_verify")

        session['req'] = req
        auth = o.authorization_url("http://fanfou.com/oauth/authorize", oauth_callback=ov)
    except:
        return main.landing(error="网络连接错误，请重试！")

    return redirect(auth)


@auth_view.route('/oauth_verify')
def oauth_verify():
    try:
        req = session['req']
        o = OAuth1Session(const.CONSUMER_KEY, const.CONSUMER_SECRET,
                          req['oauth_token'],
                          req['oauth_token_secret'], verifier=req['oauth_token'])
        ac = o.fetch_access_token("http://fanfou.com/oauth/access_token")
        session['req'] = ac
        user = o.get("http://api.fanfou.com/account/verify_credentials.json?mode=lite").json()
    except:
        return main.landing(error="验证失败，请重试！")

    try:
        try:
            ff_auth = FFAuth.query.equal_to('id', user['id']).first()
        except LeanCloudError as err:
            if err.code == 101:
                ff_auth = FFAuth()
        ff_auth.set('id', user['id'])
        ff_auth.set('nickname', user['name'])
        ff_auth.set('token', ac['oauth_token'])
        ff_auth.set('secret', ac['oauth_token_secret'])
        ff_auth.save()
    except LeanCloudError:
        return main.landing(error="LearnCloud 网络连接错误，请重试！")
    login_user(ff_auth, True)
    return redirect(url_for('main.index'))


@auth_view.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
