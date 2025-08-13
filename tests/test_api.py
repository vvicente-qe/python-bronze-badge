import datetime
import requests
import pytest
import sqlite3
from jsonschema import validate

BASE_URL = 'http://localhost:5000/api/users'
DB_PATH = '/c:/Users/VenmarVicente/Desktop/python-bronze-badge/app.db'

CRU_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "_links": {
            "type": "object",
            "properties": {
                "avatar": {"type": "string", "format": "uri"},
                "followers": {"type": "string"},
                "following": {"type": "string"},
                "self": {"type": "string"}
            },
            "required": ["avatar", "followers", "following", "self"]
        },
        "about_me": {"type": ["string", "null"]},
        "follower_count": {"type": "integer"},
        "following_count": {"type": "integer"},
        "id": {"type": "integer"},
        "last_seen": {"type": "string", "format": "date-time"},
        "post_count": {"type": "integer"},
        "username": {"type": "string"}
    },
    "required": [
        "_links",
        "follower_count",
        "following_count",
        "id",
        "last_seen",
        "post_count",
        "username"
    ]
}

READ_USER_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "_links": {
            "type": "object",
            "properties": {
                "next": {"type": ["string", "null"]},
                "prev": {"type": ["string", "null"]},
                "self": {"type": "string"}
            },
            "required": ["next", "prev", "self"]
        },
        "_meta": {
            "type": "object",
            "properties": {
                "page": {"type": "integer"},
                "per_page": {"type": "integer"},
                "total_items": {"type": "integer"},
                "total_pages": {"type": "integer"}
            },
            "required": ["page", "per_page", "total_items", "total_pages"]
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "_links": {
                        "type": "object",
                        "properties": {
                            "avatar": {"type": "string", "format": "uri"},
                            "followers": {"type": "string"},
                            "following": {"type": "string"},
                            "self": {"type": "string"}
                        },
                        "required": ["avatar", "followers", "following", "self"]
                    },
                    "about_me": {"type": ["string", "null"]},
                    "follower_count": {"type": "integer"},
                    "following_count": {"type": "integer"},
                    "id": {"type": "integer"},
                    "last_seen": {"type": "string", "format": "date-time"},
                    "post_count": {"type": "integer"},
                    "username": {"type": "string"}
                },
                "required": [
                    "_links",
                    "follower_count",
                    "following_count",
                    "id",
                    "last_seen",
                    "post_count",
                    "username"
                ]
            }
        }
    },
    "required": ["_links", "_meta", "items"]
}

def get_user_from_db(user_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, email, about_me FROM user WHERE id=?", (user_id,))
    row = cursor.fetchone()
    connection.close()
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'about_me': row[3]
        }
    return None

@pytest.fixture
def new_user():
    random_string = str(datetime.datetime.now().timestamp())
    user_data = {
        "username": f"uname_{random_string}",
        "email": f"test{random_string}@test.com",
        "about_me": f"about me{random_string}",
        "password": "test"
    }
    response = requests.post(BASE_URL, json=user_data)
    response.raise_for_status()
    assert response.status_code == 201
    data = response.json()
    yield data

def test_get_user_api():
    response = requests.get(f'{BASE_URL}/1')
    data = response.json()
    assert response.status_code == 200
    validate(instance=data, schema=CRU_USER_SCHEMA)
    assert data['username'] == 'test'
    assert data['id'] == 1

def test_get_user_list_api():
    response = requests.get(BASE_URL)
    data = response.json()
    assert response.status_code == 200
    assert data['_meta']['total_items'] > 1
    validate(instance=data, schema=READ_USER_LIST_SCHEMA)

def test_create_user_api(new_user):
    assert new_user['username'].startswith('uname_')
    assert new_user['about_me'].startswith('about me')
    validate(instance=new_user, schema=CRU_USER_SCHEMA)

    # Check in DB
    db_user = get_user_from_db(new_user['id'])
    assert db_user is not None
    assert db_user['username'] == new_user['username']

def test_edit_user_api(new_user):
    random_string = str(datetime.datetime.now().timestamp())
    user_id = new_user['id']
    updated_data = {
        "username": f"updated_username{random_string}",
        "email": f"updated_email{random_string}@test.com",
        "about_me": f"updated about me{random_string}"
    }
    response = requests.put(f"{BASE_URL}/{user_id}", json=updated_data)
    data = response.json()
    assert response.status_code == 200
    validate(instance=new_user, schema=CRU_USER_SCHEMA)
    assert data['username'] == f"updated_username{random_string}"
    assert data['about_me'] == f"updated about me{random_string}"

    # Check in DB
    db_user = get_user_from_db(user_id)
    assert db_user is not None
    assert db_user['username'] == updated_data['username']
    assert db_user['email'] == updated_data['email']
    assert db_user['about_me'] == updated_data['about_me']

def test_delete_user_api(new_user):
    user_id = new_user['id']
    response = requests.delete(f'{BASE_URL}/{user_id}')
    assert response.status_code == 200
    assert response.json()['message'] == f'User {user_id} deleted successfully.'

    # Check in DB
    db_user = get_user_from_db(user_id)
    assert db_user is None
