# encoding: utf-8
# pylint: disable=missing-docstring
from datetime import datetime

import pytest

from flask_login import current_user, login_user, logout_user

from app.modules.users import models


@pytest.fixture(autouse=True)
def patch_User_password():
    # pylint: disable=invalid-name,protected-access
    """
    By default, the application uses ``bcrypt`` to store passwords securely.
    However, ``bcrypt`` is a slow hashing algorithm (by design), so it is
    better to downgrade it to ``plaintext`` while testing, since it will save
    us quite some time.
    """
    # NOTE: It seems a hacky way, but monkeypatching is a hack anyway.
    password_field_context_config = models.User.password.property.columns[0].type.context._config
    password_field_context_config._init_scheme_list(('plaintext', ))
    password_field_context_config._init_records()
    password_field_context_config._init_default_schemes()

@pytest.fixture()
def user_instance():
    user_id = 1
    _user_instance = models.User(
        id=user_id,
        username="username",
        first_name="First Name",
        middle_name="Middle Name",
        last_name="Last Name",
        password="password",
        email="user@email.com",
        created=datetime.now(),
        updated=datetime.now(),
        is_active=True,
        is_readonly=False,
        is_admin=False,
    )
    _user_instance.get_id = lambda: user_id
    return _user_instance

@pytest.yield_fixture()
def authenticated_user_instance(flask_app):
    with flask_app.test_request_context('/'):
        login_user(user_instance())
        yield current_user
        logout_user()

@pytest.yield_fixture()
def anonymous_user_instance(flask_app):
    with flask_app.test_request_context('/'):
        yield current_user
