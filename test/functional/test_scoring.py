import pytest
import redis.exceptions

import scoring


@pytest.mark.parametrize(
    "key, expected",
    [("key", 10.5), ("test", 3.0)],
)
def test_get_score_storage_connected(mocker, storage, key, expected):
    mocker.patch("scoring.get_key", return_value=key)
    if key == "key":
        storage.cache_set(key=key, value=10.50, seconds=3600)
    got = scoring.get_score(storage, "74951111111", "test@test.com")
    assert got == expected


def test_get_score_storage_disconnected(disconnected_storage):
    got = scoring.get_score(disconnected_storage, "74951111111", "test@test.com")
    assert got == 3.0


def test_get_interests_storage_connected(storage):
    key = "i:key"
    storage.cache_set(key=key, value=10.50, seconds=3600)
    got = scoring.get_interests(storage, "key")
    assert got == 10.5


def test_get_interests_storage_disconnected(disconnected_storage):
    with pytest.raises(redis.exceptions.ConnectionError):
        scoring.get_interests(disconnected_storage, "key")
