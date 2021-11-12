import pytest
from flask import current_app

from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            assert current_app.config["ENV"] == "production"
        yield client


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Churn prediction" in response.data


def test_upload(client):
    response = client.get("/upload")
    assert response.status_code == 200
    assert b"Please select a file" in response.data


@pytest.mark.parametrize(
    "test_input,expected", [("fake_input.csv", 400), ("insurance_to_predict.csv", 200)]
)
def test_predict(client, test_input, expected):
    with client.session_transaction(subdomain="blue") as session:
        session["current_filename"] = test_input
    response = client.get("/predict", subdomain="blue")
    assert response.status_code == expected
