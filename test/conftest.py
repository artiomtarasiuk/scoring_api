import fakeredis
import pytest

from storage import Storage


@pytest.fixture(scope="session")
def storage():
    s = Storage()
    yield s
    s.client.flushdb()
    s.client.close()


@pytest.fixture(scope="session")
def fake_storage():
    s = Storage()
    server = fakeredis.FakeServer()
    server.connected = False
    s.client = fakeredis.FakeStrictRedis(server=server)
    yield s
    s.client.close()


@pytest.fixture(scope="function")
def storage_object():
    return {"key": "value"}
