import time

import pytest
import redis


def test_storage_health_check(storage):
    assert storage.health_check()


def test_disconnected_storage_health_check(fake_storage):
    with pytest.raises(redis.exceptions.ConnectionError):
        fake_storage.health_check()


def test_storage_cache_set(storage, storage_object):
    key = "key"
    storage.cache_set(key=key, value=storage_object[key], seconds=1)


def test_disconnected_storage_cache_set(fake_storage, storage_object):
    key = "key"
    result = fake_storage.cache_set(key=key, value=storage_object[key], seconds=1)
    assert not result


def test_storage_get(storage, storage_object):
    key = "key"
    to_sleep = 2
    storage.cache_set(key=key, value=storage_object[key], seconds=to_sleep)
    value = storage.get(key).decode()
    assert storage_object[key] == value
    time.sleep(to_sleep)
    assert not storage.get(key)


def test_disconnected_storage_get(fake_storage, storage_object):
    with pytest.raises(redis.exceptions.ConnectionError):
        fake_storage.get("key").decode()


def test_storage_cache_get(storage, storage_object):
    key = "key"
    to_sleep = 2
    storage.cache_set(key=key, value=storage_object[key], seconds=to_sleep)
    value = storage.cache_get(key).decode()
    assert storage_object[key] == value
    time.sleep(to_sleep)
    assert not storage.cache_get(key)


def test_disconnected_storage_cache_get(fake_storage, storage_object):
    result = fake_storage.cache_get("key")
    assert not result
