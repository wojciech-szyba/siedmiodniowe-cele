import pytest
from ..app import create_app
from ..models import User

@pytest.fixture
def app_test():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def app_ctx(app_test):  # use app_test, not app
    with app_test.app_context():
        yield

@pytest.fixture
def client(app_test):
    return app_test.test_client()

@pytest.fixture
def authenticated_client(client, app_test):  # inject app_test here
    with app_test.app_context():
        user = User(id=3, username='test', email="test@example.com")
    return client

def test_home_route(authenticated_client):
    response = authenticated_client.get("/", follow_redirects=True)
    print(response.data)
    assert response.status_code == 200

def test_daily_route(authenticated_client):
    response = authenticated_client.get("/daily/", follow_redirects=True)
    assert response.status_code == 200

def test_new_goal_route(authenticated_client):
    response = authenticated_client.get("/add_goal/2025-03-01/1/", follow_redirects=True)
    assert response.status_code == 200

def test_update_goal_route(authenticated_client):
    response = authenticated_client.get("/update_goal/1", follow_redirects=True)
    assert response.status_code == 200

def test_delete_goal_route(authenticated_client):
    response = authenticated_client.get("/delete_goal/1", follow_redirects=True)
    assert response.status_code == 200
