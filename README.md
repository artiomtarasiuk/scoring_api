# scoring_api

Scoring api.

## Setup (optional)

 - Setup python 3.8 venv
 - Install poetry `pip install poetry==1.1.11`
 - Run `poetry install --no-root` to install dependencies (optional)

## Usage

To start the http server with default params (port 8080 and no logs storage): `python3 api.py`

To use custom params (e.g. port 8081 and logs persistence to logs.txt): `python api.py -p 9000 -l logs.txt`

## Requests

### online_score endpoint

Request example:
```shell
curl -X POST -H "Content-Type: application/json" -d '{"account": "artiom", "token": "b35f03795b596e841890d20400da50a204d4763a86cc5409a6e2db842323fa8e877bd8aa33b97994a370e8856e5ded7bd2e72ff86b8d7525d0d033173ce65919", "login": "artiom", "method": "online_score", "arguments": {"phone": 79999999999, "email": "artiom@email.com" }}' localhost:8080/method
```

### clients_interests endpoint

Request example:
```shell
curl -X POST -H "Content-Type: application/json" -d '{"account": "artiom", "login": "artiom", "method": "clients_interests", "token":"b35f03795b596e841890d20400da50a204d4763a86cc5409a6e2db842323fa8e877bd8aa33b97994a370e8856e5ded7bd2e72ff86b8d7525d0d033173ce65919", "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' localhost:8080/method/
```

# Testing

Go to optional `Setup` step above and follow the instructions.

Run `make test` to launch the tests with formatting check.
