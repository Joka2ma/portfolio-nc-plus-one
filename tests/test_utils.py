import bcrypt
import pytest

from src.utils import hash_password, normalise_email, parse_id, validate_event_times,verify_password


def test_lowercase_email() -> None:
    assert normalise_email("DavId@example.com") == "david@example.com"


def test_remove_whitespaces() -> None:
    assert normalise_email(" david@example.com ") == "david@example.com"


def test_password_is_hashed() -> None:
    new_password = hash_password("password123")

    assert new_password != "password123"
    assert bcrypt.checkpw(b"password123", new_password.encode())


def test_raises_if_end_before_start_on_same_day() -> None:
    with pytest.raises(ValueError):
        validate_event_times("2026-07-04T20:00:00+01:00", "2026-07-04T17:00:00+01:00")


def test_accepts_end_after_start_on_same_day() -> None:
    validate_event_times("2026-07-04T17:00:00+01:00", "2026-07-04T20:00:00+01:00")


def test_accepts_end_equal_to_start() -> None:
    validate_event_times("2026-07-04T17:00:00+01:00", "2026-07-04T17:00:00+01:00")


def test_accepts_end_on_a_later_day() -> None:
    validate_event_times("2026-07-04T22:00:00+01:00", "2026-07-05T02:00:00+01:00")


def test_raises_on_invalid_date_string() -> None:
    with pytest.raises(ValueError):
        validate_event_times("not a date", "2026-07-04T17:00:00+01:00")


@pytest.mark.parametrize(
    "raw, expected",
    [("1", 1), ("2", 2), ("42", 42), ("0", 0), ("-3", -3), ("007", 7)],
)
def test_parse_id_accepts_integers(raw: str, expected: int) -> None:
    assert parse_id(raw) == expected


@pytest.mark.parametrize(
    "raw", ["abc", "1.5", "", "1_0", " 2", "2 ", "+", "-", "1e3", "2abc"]
)
def test_parse_id_rejects_non_integers(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_id(raw)
        
""" Verifying password and email for authentication """

def test_verify_password_is_correct_passowrd() -> None:
    assert verify_password("password123",hash_password("password123")) is True
    
    
def test_verify_password_rejects_incorrect_password() -> None:
    assert verify_password("password", hash_password("password123")) is False


