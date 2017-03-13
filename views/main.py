from flask import Blueprint
from flask import render_template
from flask_login import login_required
from flask_login import current_user
import random
from models import FFProduct


main_view = Blueprint('main', __name__)


@main_view.route('/', methods=['GET'])
@login_required
def index():
    nickname = current_user.get('nickname')
    products = FFProduct.query.find()
    product_list = []
    for product in products:
        image_list = []
        for image in product.get('images'):
            image_list.append(image)
        product_item = {'name': product.get('name'),
                        'desc': product.get('intro'),
                        'img': image_list}
        product_list.append(product_item.copy())
    random.shuffle(product_list)
    voted = [False] * len(products)

    return render_template('index.html',
                           data=product_list,
                           voted=voted,
                           nickname=nickname)


@main_view.route("/landing")
def landing(error=""):
    return render_template('oauth.html', error=error)

  
@main_view.route('/vote', methods=['POST'])
def vote():
    pass
