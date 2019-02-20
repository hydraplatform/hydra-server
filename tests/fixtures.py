#Fixtures.py
import pytest
from hydra_client.connection import RemoteJSONConnection

@pytest.fixture()
def client():
    client=RemoteJSONConnection("http://localhost:8080/json")
    client.login("root","")
    return client
