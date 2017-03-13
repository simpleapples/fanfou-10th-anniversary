from flask import Blueprint
from flask import render_template
from flask_login import login_required
from flask_login import current_user
import random


main_view = Blueprint('main', __name__)


@main_view.route('/', methods=['GET'])
@login_required
def index():
    nickname = current_user.get('nickname')
    o = {
            "name": "测试设计 %d",
            "desc": "测试设计介绍 %d",
            "img": [
                "http://placehold.it/450x300?text=Design+{id}+(0)",
                "http://placehold.it/450x300?text=Design+{id}+(1)",
                "http://placehold.it/450x300?text=Design+{id}+(2)"
            ]
        }
    l = []
    WORKS = 10

    for i in range(WORKS):
        l.append(o.copy())
        l[-1]['name'] %= i
        l[-1]['desc'] %= i
        l[-1]['img'] = [j.format(id=i) for j in l[-1]['img']]

    l = random.shuffle(l)
    # list of bools: if user has voted the entry
    voted = [False] * WORKS

    return render_template('index.html',
                           data=l,
                           voted=voted,
                           nickname=nickname)


@main_view.route("/landing")
def landing(error=""):
    return render_template('oauth.html', error=error)
