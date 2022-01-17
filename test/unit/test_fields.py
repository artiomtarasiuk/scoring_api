import pytest

import api


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        (None, True, False),
        (None, True, True),
    ],
)
def test_base_validation_required_invalid(value, required, nullable):
    field = api.BaseValidation(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        (1, True, False),
        ("a", True, True),
        (None, False, True),
    ],
)
def test_base_validation_required_valid(value, required, nullable):
    field = api.BaseValidation(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "required, nullable",
    [
        (True, False),
    ],
)
def test_base_validation_nullable_invalid(required, nullable):
    field = api.BaseValidation(required, nullable)
    for value in api.NULL_VALUES:
        with pytest.raises(api.CustomValidationError) as e:
            field.validate(value)


@pytest.mark.parametrize(
    "required, nullable",
    [
        (False, True),
    ],
)
def test_base_validation_nullable_valid(required, nullable):
    field = api.BaseValidation(required, nullable)
    for value in api.NULL_VALUES:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        (1, True, True),
        (1.5, True, True),
        ([], True, True),
        ({}, True, True),
    ],
)
def test_char_field_invalid(value, required, nullable):
    field = api.CharField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("a", False, False),
        ("a", True, False),
        ("a", False, True),
        ("a", True, True),
    ],
)
def test_char_field_valid(value, required, nullable):
    field = api.CharField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("a", True, True),
        (1, True, True),
        (1.5, True, True),
        ([], True, True),
    ],
)
def test_arguments_field_invalid(value, required, nullable):
    field = api.ArgumentsField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ({"a": 1}, False, False),
        ({"a": 1}, True, False),
        ({}, False, True),
        ({}, True, True),
    ],
)
def test_arguments_field_valid(value, required, nullable):
    field = api.ArgumentsField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("a", True, True),
    ],
)
def test_email_field_invalid(value, required, nullable):
    field = api.EmailField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("@", True, True),
    ],
)
def test_email_field_valid(value, required, nullable):
    field = api.EmailField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        (111.55, True, True),
        ("+7495111111", True, True),
        ("6495111111", True, True),
        (6495111111, True, True),
        ("7495111111", True, True),
        (7495111111, True, True),
    ],
)
def test_phone_field_invalid(value, required, nullable):
    field = api.PhoneField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("74951111110", True, True),
        (74951111110, True, True),
    ],
)
def test_phone_field_valid(value, required, nullable):
    field = api.PhoneField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        (111, True, True),
        (111.55, True, True),
        ("2020", True, True),
        ("2020-01-01", True, True),
        ("2020/01/01", True, True),
        ("01/12/2022", True, True),
    ],
)
def test_date_field_invalid(value, required, nullable):
    field = api.DateField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("01.12.2022", True, True),
    ],
)
def test_date_field_valid(value, required, nullable):
    field = api.DateField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("01.01.1951", True, True),
    ],
)
def test_birth_day_field_invalid(value, required, nullable):
    field = api.BirthDayField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("01.01.1992", True, True),
    ],
)
def test_birth_day_field_valid(value, required, nullable):
    field = api.BirthDayField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("1", True, True),
        (-1, True, True),
        (4, True, True),
    ],
)
def test_gender_field_invalid(value, required, nullable):
    field = api.GenderField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        (0, True, True),
        (1, True, True),
        (2, True, True),
    ],
)
def test_gender_field_valid(value, required, nullable):
    field = api.GenderField(required, nullable)
    field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ("1", True, True),
        (-1, True, True),
        ({0, 1, 2}, True, True),
        ((0, 1, 2), True, True),
    ],
)
def test_client_ids_field_invalid(value, required, nullable):
    field = api.ClientIDsField(required, nullable)
    with pytest.raises(api.CustomValidationError) as e:
        field.validate(value)


@pytest.mark.parametrize(
    "value, required, nullable",
    [
        ([0], True, True),
        ([0,1,2], True, True),
    ],
)
def test_client_ids_field_valid(value, required, nullable):
    field = api.ClientIDsField(required, nullable)
    field.validate(value)
