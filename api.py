#!/usr/bin/env python3

import datetime
import hashlib
import json
import logging
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from typing import Any, Dict, Tuple

from scoring import get_interests, get_score
from storage import Storage

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
BIRTHDAY_DIFF = 70
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
NULL_VALUES = [None, "", [], {}, ()]


class CustomValidationError(Exception):
    """Custom validation exception"""

    def __init__(self, code: int, error: str):
        self.code = code
        self.error = error


class BaseValidation:
    def __init__(self, required: bool, nullable: bool):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        if self.required and value is None:
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Field {self.__class__.__name__} is required",
            )
        if not self.nullable and value in NULL_VALUES:
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Field {self.__class__.__name__} cannot be nullable",
            )


class CharField(BaseValidation):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, str):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Expected `str` type for field {self.__class__.__name__}",
            )


class ArgumentsField(BaseValidation):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, dict):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Expected `dict` type for field {self.__class__.__name__}",
            )


class EmailField(CharField):
    def validate(self, value):
        super().validate(value)
        if "@" not in value:
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Unable to parse email string for field {self.__class__.__name__}",
            )


class PhoneField(BaseValidation):
    def validate(self, value):
        super().validate(value)
        if not value:
            return
        if not (isinstance(value, str) or isinstance(value, int)):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Expected `str` or `int` type for field {self.__class__.__name__}",
            )
        value_str = str(value)
        if not value_str.isdigit():
            raise CustomValidationError(
                code=INVALID_REQUEST, error=f"Phone number should have only digits"
            )
        if not value_str.startswith("7"):
            raise CustomValidationError(
                code=INVALID_REQUEST, error=f"Phone number should begin with 7"
            )
        if len(value_str) != 11:
            raise CustomValidationError(
                code=INVALID_REQUEST, error=f"Phone number should have 11 digits only"
            )


class DateField(BaseValidation):
    def validate(self, value):
        super().validate(value)
        if not value:
            return
        if not isinstance(value, str):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Expected `str` type for field {self.__class__.__name__}",
            )
        try:
            return self.parse_date(value)
        except ValueError:
            raise CustomValidationError(
                code=INVALID_REQUEST, error="Dates should have 'DD.MM.YYYY' format"
            )

    @staticmethod
    def parse_date(value: str) -> datetime.date:
        return datetime.datetime.strptime(value, "%d.%m.%Y").date()


class BirthDayField(DateField):
    def validate(self, value):
        super().validate(value)
        dt = super().parse_date(value)
        if not dt:
            return
        # this is just reasonable approximation, not 100% accurate
        years_diff = int((datetime.datetime.utcnow().date() - dt).days / 365.2425)
        if years_diff > BIRTHDAY_DIFF:
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Birthday should not be older than {BIRTHDAY_DIFF} years",
            )


class GenderField(BaseValidation):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, int):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Expected `int` type for field {self.__class__.__name__}",
            )
        if value not in GENDERS.keys():
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Gender can be one of the range values: {list(GENDERS.keys())}",
            )


class ClientIDsField(BaseValidation):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, list):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error=f"Expected `list` type for field {self.__class__.__name__}",
            )
        if not all(isinstance(v, int) for v in value):
            raise CustomValidationError(
                code=INVALID_REQUEST,
                error="Expected `int` for all values of ClientIDs",
            )


class BaseRequest:
    def __init__(self, body: Dict[str, Any]):
        self.body = body

    def validate(self) -> None:
        """Validate request"""
        for field_name, _type in self.__class__.__dict__.items():
            if not isinstance(_type, BaseValidation):
                continue
            field = getattr(self, field_name)
            field_value = self.body.get(field_name)
            setattr(self, field_name, field_value)
            # validate the field if required
            if not field.required and field_name not in self.body:
                continue
            field.validate(field_value)


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        super().validate()
        pairs = [
            (self.phone, self.email),
            (self.first_name, self.last_name),
            (self.gender, self.birthday),
        ]
        for pair in pairs:
            if all(value not in NULL_VALUES for value in pair):
                return
        raise CustomValidationError(
            code=INVALID_REQUEST,
            error="Request should have at least one non-null pair of phone-email, first_name-last_name or gender-birthday",
        )


def check_auth(request: MethodRequest) -> bool:
    if request.is_admin:
        hash_str = datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
        digest = hashlib.sha512(hash_str.encode("utf-8")).hexdigest()
    else:
        hash_str = request.account + request.login + SALT
        digest = hashlib.sha512(hash_str.encode("utf-8")).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(
    method_request: MethodRequest, ctx: Dict[str, Any], store
) -> Tuple[Any, int, Dict[str, Any]]:
    method_args = method_request.arguments
    ctx["has"] = [k for k, v in method_args.items() if v not in NULL_VALUES]

    if method_request.is_admin:
        return {"score": 42}, OK, ctx

    req = OnlineScoreRequest(method_args)
    bd = req.birthday
    req.validate()
    score = get_score(
        store,
        phone=req.phone,
        email=req.email,
        birthday=bd.parse_date(req.birthday) if req.birthday else None,
        gender=req.gender,
        first_name=req.first_name,
        last_name=req.last_name,
    )
    return {"score": score}, OK, ctx


def clients_interests_handler(
    method_request: MethodRequest, ctx: Dict[str, Any], store
) -> Tuple[Any, int, Dict[str, Any]]:
    req = ClientsInterestsRequest(method_request.arguments)
    req.validate()
    ctx["nclients"] = len(req.client_ids)
    response = dict()
    for client_id in req.client_ids:
        response[client_id] = get_interests(store, client_id)
    return response, OK, ctx


def method_handler(
    request: Dict[str, Any], ctx: Dict[str, Any], store
) -> Tuple[Any, int, Dict[str, Any]]:
    routers = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler,
    }
    try:
        method_request = MethodRequest(request["body"])
        method_request.validate()
        if not check_auth(method_request):
            return None, FORBIDDEN, ctx
        method = method_request.method
        if method not in routers:
            return f"Not found for {method}", NOT_FOUND, ctx
        response, code, ctx = routers[method](method_request, ctx, store)
    except CustomValidationError as e:
        return e.error, e.code, ctx
    else:
        return response, code, ctx


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = Storage(socket_timeout=120, socket_connect_timeout=60)

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code, context = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
