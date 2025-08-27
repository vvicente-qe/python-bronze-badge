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
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "about_me": {"type": ["string", "null"]}
    },
    "required": [
        "id",
        "username",
        "email"
    ]
}
READ_USER_LIST_SCHEMA = {
    "type": "object",
    "properties": {
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
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "about_me": {"type": ["string", "null"]}
                },
                "required": ["id", "username", "email"]
            }
        }
    },
    "required": ["_meta", "items"]
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

user_cache = {}

@pytest.fixture(scope="module")
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
    user_cache["user"] = data
    yield data

def test_create_user_api(new_user):
    validate(instance=new_user, schema=CRU_USER_SCHEMA)

    # Check in DB
    db_user = get_user_from_db(new_user['id'])
    assert db_user is not None
    assert db_user['id'] == new_user['id']
    assert db_user['username'] == new_user['username']
    assert db_user['email'] == new_user['email']
    assert db_user['about_me'] == new_user['about_me']

def test_get_user_api():
    user = user_cache["user"]
    user_id = user['id']
    response = requests.get(f'{BASE_URL}/{user_id}')
    data = response.json()
    db_user = get_user_from_db(user_id)
    validate(instance=data, schema=CRU_USER_SCHEMA)

    assert response.status_code == 200
    assert data['id'] == user['id'] == db_user['id']
    assert data['username'] == user['username'] == db_user['username']
    assert data['email'] == user['email'] == db_user['email']
    assert data['about_me'] == user['about_me'] == db_user['about_me']


def test_get_user_list_api():
    response = requests.get(BASE_URL)
    data = response.json()
    validate(instance=data, schema=READ_USER_LIST_SCHEMA)
    assert response.status_code == 200
    assert data['_meta']['total_items'] > 0


def test_edit_user_api():
    user = user_cache["user"]
    user_id = user['id']

    random_string = str(datetime.datetime.now().timestamp())
    updated_data = {
        "username": f"updated_username{random_string}",
        "email": f"updated_email{random_string}@test.com",
        "about_me": f"updated about me{random_string}"
    }

    response = requests.put(f"{BASE_URL}/{user_id}", json=updated_data)
    data = response.json()
    db_user = get_user_from_db(user_id)
    validate(instance=data, schema=CRU_USER_SCHEMA)

    assert response.status_code == 200
    assert data['username'] == f"updated_username{random_string}" == db_user['username']
    assert data['email'] == f"updated_email{random_string}@test.com" == db_user['email']
    assert data['about_me'] == f"updated about me{random_string}" == db_user['about_me']

def test_delete_user_api():
    user = user_cache["user"]
    user_id = user['id']
    response = requests.delete(f'{BASE_URL}/{user_id}')
    assert response.status_code == 200
    assert response.json()['message'] == f'User {user_id} deleted successfully.'

    # Check in DB
    db_user = get_user_from_db(user_id)
    assert db_user is None
