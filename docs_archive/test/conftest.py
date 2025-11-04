import os
import sys
import pytest

ORIG_DIR = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)
from app import app as flask_app
os.chdir(ORIG_DIR)

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client
