import pytest
from fastapi.testclient import TestClient
from main import app, devices
from hardware.fake import FakeDevice

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_fake_device():
    devices["test1"] = FakeDevice()
    yield
    devices.clear()


def test_measure_valid_channel():
    response = client.post("/devices/test1/measure", json={"channel": "0"})
    assert response.status_code == 200
    assert response.json()["voltage"] == 3.30


def test_measure_invalid_channel():
    response = client.post("/devices/test1/measure", json={"channel": "99"})
    assert response.status_code == 502


def test_measure_unknown_device():
    response = client.post("/devices/ghost/measure", json={"channel": "0"})
    assert response.status_code == 404


def test_list_devices():
    response = client.get("/devices")
    assert "test1" in response.json()["devices"]