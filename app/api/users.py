import sqlalchemy as sa
from flask import request, url_for, abort, jsonify
from app import db
from app.models import User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
import json

def json_response(data, status=200, headers=None):
    response = jsonify(data)
    response.status_code = status
    if headers:
        response.headers.extend(headers)
    # test_response = json.dumps(response.get_json(), indent=4)
    return response


@bp.route('/users/<int:id>', methods=['GET'])
# @token_auth.login_required
def get_user(id):
    result = db.get_or_404(User, id).to_dict()
    db.session.close()
    return json_response(result, 200)

@bp.route('/users', methods=['GET'])
# @token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    result = User.to_collection_dict(sa.select(User), page, per_page, 'api.get_users')
    db.session.close()
    return json_response(result, 200)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        return bad_request('please use a different username')
    if db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    headers = {'Location': url_for('api.get_user', id=user.id)}
    db.session.close()
    return json_response(user.to_dict(), 201, headers)

@bp.route('/users/<int:id>', methods=['PUT'])
# @token_auth.login_required
def update_user(id):
    # if token_auth.current_user().id != id:
    #     abort(403)
    user = db.get_or_404(User, id)
    data = request.get_json()
    if 'username' in data and data['username'] != user.username and \
        db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
        db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    result = user.to_dict()
    db.session.close()
    return json_response(result, 200)

@bp.route('/users/<int:id>', methods=['DELETE'])
# @token_auth.login_required
def delete_user(id):
    user = db.get_or_404(User, id)
    db.session.delete(user)
    db.session.commit()
    db.session.close()
    return json_response({'message': f'User {id} deleted successfully.'}, 200)