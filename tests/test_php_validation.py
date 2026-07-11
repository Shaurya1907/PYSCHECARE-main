import json
import shutil
import subprocess

import pytest


PHP = shutil.which("php")


pytestmark = pytest.mark.skipif(PHP is None, reason="PHP CLI is not available")


def run_php(expression):
    code = (
        "require 'validation.php'; "
        f"$result = {expression}; "
        "echo json_encode($result);"
    )
    completed = subprocess.run(
        [PHP, "-r", code],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_valid_signup_data():
    expression = "validateSignupInput('valid_user', 'user@example.com', 'password123')"
    assert run_php(expression) is None


def test_signup_rejects_invalid_email():
    expression = "validateSignupInput('valid_user', 'bad-email', 'password123')"
    assert run_php(expression) == "email"


def test_signup_rejects_long_username():
    expression = (
        "validateSignupInput("
        "str_repeat('a', 51), 'user@example.com', 'password123'"
        ")"
    )
    assert run_php(expression) == "username"


def test_signup_rejects_weak_password():
    expression = "validateSignupInput('valid_user', 'user@example.com', 'short')"
    assert run_php(expression) == "weak_password"


def test_contact_form_validation():
    expression = (
        "validateContactInput("
        "'Ava', 'ava@example.com', 'Checking in', 'Hello there'"
        ")"
    )
    assert run_php(expression) is None

    expression = (
        "validateContactInput('', 'ava@example.com', 'Checking in', 'Hello there')"
    )
    assert (
        run_php(expression)
        == "Please enter your name under 100 characters."
    )

    expression = (
        "validateContactInput('Ava', 'bad-email', 'Checking in', 'Hello there')"
    )
    assert (
        run_php(expression)
        == "Please enter a valid email address."
    )

    expression = "validateContactInput('Ava', 'ava@example.com', '', 'Hello there')"
    assert (
        run_php(expression)
        == "Please enter a subject under 255 characters."
    )

    expression = (
        "validateContactInput("
        "'Ava', 'ava@example.com', str_repeat('x', 256), 'Hello there'"
        ")"
    )
    assert (
        run_php(expression)
        == "Please enter a subject under 255 characters."
    )

    expression = (
        "validateContactInput("
        "'Ava', 'ava@example.com', 'Checking in', str_repeat('x', 1001)"
        ")"
    )
    assert (
        run_php(expression)
        == "Please enter a message under 1000 characters."
    )
