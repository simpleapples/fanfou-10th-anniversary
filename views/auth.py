# coding: utf-8

from leancloud import Object
from leancloud import LeanCloudError
from flask import Blueprint
from flask import render_template
import fanfou
from forms.auth import AuthForm
import const


class FFAuth(Object):
    pass

auth_view = Blueprint('auth', __name__)


@auth_view.route('/auth', methods=['GET', 'POST'])
def xauth():
    form = AuthForm()
    error = ''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        consumer = {'key': const.CONSUMER_KEY,
                    'secret': const.CONSUMER_SECRET}
        client = fanfou.XAuth(consumer, email, password)

        ff_auth = FFAuth(email=email,
                         token=client.oauth_token['key'].decode('utf-8'),
                         secret=client.oauth_token['secret'].decode('utf-8'))
        try:
            ff_auth.save()
        except LeanCloudError as _:
            error = '写入数据库失败'
    else:
        error = '表单非法'
    return render_template('auth.html',
                           error=error)
