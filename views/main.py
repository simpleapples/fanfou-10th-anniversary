from leancloud import LeanCloudError
from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
from flask_login import login_required
from flask_login import current_user
import random
import datetime
from models import FFProduct
from models import FFVote
from models import FFAuth
import const


main_view = Blueprint('main', __name__)


@main_view.route('/rank', methods=['GET'])
@main_view.route('/', methods=['GET'])
@login_required
def index():
    list_type = 'rank'
    if not request.path.startswith('/rank'):
        list_type = 'index'

    if list_type == 'index' and datetime.datetime.utcnow() > datetime.datetime(2017, 3, 16, 16, 0, 0):
        return redirect('/rank')
    nickname = current_user.get('nickname')
    products = FFProduct.query.add_descending('vote').find()
    vote_result = current_user.get('voteResult')
    product_list = []
    voted = {}
    for product in products:
        image_list = []
        for image in product.get('images'):
            image_list.append(image)
        author_names = product.get('authorName').split(',')
        author_sites = product.get('authorSite').split(',')
        authors = []
        if len(author_names) == len(author_sites):
            for i, author_name in enumerate(author_names):
                authors.append({'nickname': author_name,
                                'site': author_sites[i]})
        product_item = {'id': product.id,
                        'name': product.get('name'),
                        'desc': product.get('intro'),
                        'vote': product.get('vote'),
                        'authors': authors,
                        'img': image_list}
        product_list.append(product_item.copy())

        if product.id in vote_result:
            voted[product.id] = True
        else:
            voted[product.id] = False

    if list_type == 'index':
        random.shuffle(product_list)

    return render_template('index.html',
                           data=product_list,
                           voted=voted,
                           nickname=nickname,
                           list_type=list_type)


@main_view.route('/products/<string:product_id>/<string:action>', methods=['POST'])
@login_required
def vote(product_id, action):
    if datetime.datetime.utcnow() > datetime.datetime(2017, 3, 16, 16, 0, 0):
        return jsonify({'success': False,
                        'error': '投票已截止'})

    if action == 'vote':
        ff_vote_count = FFVote.query.equal_to('authUser', current_user).count()
        if ff_vote_count >= const.VOTE_LIMIT:
            return jsonify({'success': False,
                            'error': '最多只能投 ' + str(const.VOTE_LIMIT) + ' 票'})

    try:
        ff_product = FFProduct.query.get(product_id)
    except LeanCloudError as _:
        return jsonify({'success': False,
                        'error': '没有查询到该作品'})

    try:
        ff_auth = FFAuth.query.get(current_user.id)
    except LeanCloudError as _:
        return jsonify({'success': False,
                        'error': '没有查询到该用户'})

    ff_vote = None
    try:
        ff_vote = FFVote.query.equal_to('authUser', ff_auth).equal_to('targetProduct', ff_product).first()
    except LeanCloudError as _:
        pass

    if action == 'vote':
        if ff_vote:
            return jsonify({'success': False,
                            'error': '已经投过'})
        try:
            ff_vote = FFVote()
            ff_vote.set('authUser', ff_auth)
            ff_vote.set('targetProduct', ff_product)
            ff_vote.save()
        except LeanCloudError as _:
            return jsonify({'success': False,
                            'error': '写入数据库失败'})
        try:
            vote_count = ff_product.get('vote') + 1
            ff_product.set('vote', vote_count)
            ff_product.save()

            vote_result = current_user.get('voteResult')
            if ff_product.id not in vote_result:
                vote_result.append(ff_product.id)
                current_user.set('voteResult', vote_result)
                current_user.save()
        except LeanCloudError as _:
            pass

        return jsonify({'success': True,
                        'error': ''})

    if action == 'undo':
        if not ff_vote:
            return jsonify({'success': True,
                            'error': ''})
        try:
            ff_vote.destroy()
        except LeanCloudError as _:
            return jsonify({'success': False,
                            'error': '删除失败'})

        try:
            vote_count = ff_product.get('vote') - 1
            ff_product.set('vote', vote_count)
            ff_product.save()

            vote_result = current_user.get('voteResult')
            if ff_product.id in vote_result:
                vote_result.remove(ff_product.id)
                current_user.set('voteResult', vote_result)
                current_user.save()
        except LeanCloudError as _:
            pass
        return jsonify({'success': True,
                        'error': ''})
