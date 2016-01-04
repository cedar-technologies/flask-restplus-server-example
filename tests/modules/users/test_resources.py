# pylint: disable=missing-docstring
import pytest


@pytest.mark.parametrize('http_method,http_path', (
    ('GET', '/api/v1/users/'),
    ('GET', '/api/v1/users/1'),
    ('PATCH', '/api/v1/users/1'),
    ('GET', '/api/v1/users/me'),
))
def test_unauthorized_access(http_method, http_path, flask_app_client):
    response = flask_app_client.open(method=http_method, path=http_path)
    assert response.status_code == 401

def test_signup_form(flask_app_client):
    response = flask_app_client.get('/api/v1/users/signup_form')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert set(response.json.keys()) == {"recaptcha_server_key"}

def create_new_user(flask_app_client, data):
    _data = {
        'recaptcha_key': "secret_key",
    }
    _data.update(data)
    response = flask_app_client.post('/api/v1/users/', data=_data)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert {'id', 'username'} <= set(response.json.keys())
    return response.json['id']

def test_new_user_creation(flask_app_client, db):
    # pylint: disable=invalid-name
    user_id = create_new_user(
        flask_app_client,
        data={
            'username': "user1",
            'email': "user1@email.com",
            'password': "user1_password",
        }
    )
    assert isinstance(user_id, int)

    from app.modules.users.models import User

    user1_instance = User.query.get(user_id)
    assert user1_instance.username == "user1"
    assert user1_instance.email == "user1@email.com"
    assert user1_instance.password == "user1_password"

    db.session.delete(user1_instance)
    db.session.commit()
