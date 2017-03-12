from flask import Flask, render_template
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/vote')
def vote():
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

    # list of bools: if user has voted the entry
    voted = [False] * WORKS

    return render_template('vote.html', data=l, voted=voted)
