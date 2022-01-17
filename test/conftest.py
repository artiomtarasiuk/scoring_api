import json
import random
from typing import List

import fakeredis
import pytest

from storage import Storage


@pytest.fixture(scope="session")
def storage():
    s = Storage()
    server = fakeredis.FakeServer()
    s.client = fakeredis.FakeRedis(server=server)
    insert_interests_data(s, [0, 1, 2, 3])
    yield s
    s.client.flushdb()
    s.client.close()


def insert_interests_data(storage: Storage, cid_list: List[int]):
    interests = ["books", "music", "cinema", "sport"]
    for cid in cid_list:
        key = "i:%s" % cid
        storage.client.set(key, json.dumps(random.sample(interests, 2)))


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
