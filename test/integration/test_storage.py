import time

import pytest
import redis


def test_storage_health_check(storage):
    assert storage.health_check()


def test_disconnected_storage_health_check(disconnected_storage):
    with pytest.raises(redis.exceptions.ConnectionError):
        disconnected_storage.health_check()


def test_storage_cache_set(storage, storage_object):
    key = "key"
    assert storage.cache_set(key=key, value=storage_object[key], seconds=1)


def test_disconnected_storage_cache_set(disconnected_storage, storage_object):
    key = "key"
    result = disconnected_storage.cache_set(
        key=key, value=storage_object[key], seconds=1
    )
    assert not result


def test_storage_get(storage, storage_object):
    key = "key"
    to_sleep = 2
    storage.cache_set(key=key, value=storage_object[key], seconds=to_sleep)
    value = storage.get(key).decode()
    assert storage_object[key] == value
    time.sleep(to_sleep)
    assert not storage.get(key)


def test_disconnected_storage_get(disconnected_storage, storage_object):
    with pytest.raises(redis.exceptions.ConnectionError):
        disconnected_storage.get("key").decode()


def test_storage_cache_get(storage, storage_object):
    key = "key"
    to_sleep = 2
    storage.cache_set(key=key, value=storage_object[key], seconds=to_sleep)
    value = storage.cache_get(key).decode()
    assert storage_object[key] == value
    time.sleep(to_sleep)
    assert not storage.cache_get(key)


def test_disconnected_storage_cache_get(disconnected_storage, storage_object):
    result = disconnected_storage.cache_get("key")
    assert not result
