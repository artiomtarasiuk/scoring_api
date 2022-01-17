import fakeredis
import pytest

from storage import Storage


@pytest.fixture(scope="session")
def storage():
    s = Storage()
    server = fakeredis.FakeServer()
    s.client = fakeredis.FakeRedis(server=server)
    yield s
    s.client.flushdb()
    s.client.close()


@pytest.fixture(scope="session")
def disconnected_storage():
    s = Storage()
    server = fakeredis.FakeServer()
    server.connected = False
    s.client = fakeredis.FakeRedis(server=server)
    yield s
    s.client.close()


@pytest.fixture(scope="function")
def storage_object():
    return {"key": "value"}
