import datetime
import hashlib

import pytest

import api


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        msg = datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT
        request["token"] = hashlib.sha512(msg.encode("utf-8")).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg.encode("utf-8")).hexdigest()


def test_empty_request(storage):
    _, code, _ = api.method_handler({"body": {}, "headers": {}}, {}, storage)
    assert api.INVALID_REQUEST == code


@pytest.mark.parametrize(
    "req",
    [
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "",
            "arguments": {},
        },
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "sdd",
            "arguments": {},
        },
        {
            "account": "horns&hoofs",
            "login": "admin",
            "method": "online_score",
            "token": "",
            "arguments": {},
        },
    ],
)
def test_bad_auth(req, storage):
    _, code, _ = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.FORBIDDEN == code


@pytest.mark.parametrize(
    "req",
    [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ],
)
def test_invalid_method_request(req, storage):
    set_valid_auth(req)
    response, code, _ = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.1890",
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "XXX",
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": 1,
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "s",
            "last_name": 2,
        },
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ],
)
def test_invalid_score_request(arguments, storage):
    req = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "arguments": arguments,
    }
    set_valid_auth(req)
    response, code, _ = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    "arguments",
    [
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "a",
            "last_name": "b",
        },
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "a",
            "last_name": "b",
        },
    ],
)
def test_ok_score_request(arguments, storage):
    req = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "arguments": arguments,
    }
    set_valid_auth(req)
    response, code, ctx = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.OK == code
    score = response.get("score")
    assert isinstance(score, (int, float))
    assert score >= 0
    assert sorted(ctx["has"]), sorted(arguments.keys())


def test_ok_score_admin_request(storage):
    arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
    req = {
        "account": "horns&hoofs",
        "login": "admin",
        "method": "online_score",
        "arguments": arguments,
    }
    set_valid_auth(req)
    response, code, _ = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.OK == code
    score = response.get("score")
    assert score == 42


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ],
)
def test_invalid_interests_request(arguments, storage):
    req = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "clients_interests",
        "arguments": arguments,
    }
    set_valid_auth(req)
    response, code, _ = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "client_ids": [1, 2, 3],
            "date": datetime.datetime.today().strftime("%d.%m.%Y"),
        },
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ],
)
def test_ok_interests_request(arguments, storage):
    req = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "clients_interests",
        "arguments": arguments,
    }
    set_valid_auth(req)
    response, code, ctx = api.method_handler({"body": req, "headers": {}}, {}, storage)
    assert api.OK == code
    assert len(arguments["client_ids"]) == len(response)
    assert all(
        v and isinstance(v, list) and all(isinstance(i, str) for i in v)
        for v in response.values()
    )
    assert ctx.get("nclients") == len(arguments["client_ids"])
