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
    assert run_php("validateSignupInput('valid_user', 'user@example.com', 'password123')") is None


def test_signup_rejects_invalid_email():
    assert run_php("validateSignupInput('valid_user', 'bad-email', 'password123')") == "email"


def test_signup_rejects_long_username():
    assert run_php("validateSignupInput(str_repeat('a', 51), 'user@example.com', 'password123')") == "username"


def test_signup_rejects_weak_password():
    assert run_php("validateSignupInput('valid_user', 'user@example.com', 'short')") == "weak_password"


def test_contact_form_validation():
    assert run_php("validateContactInput('Ava', 'ava@example.com', 'Hello there')") is None
    assert run_php("validateContactInput('', 'ava@example.com', 'Hello there')") == "Please enter your name."
    assert run_php("validateContactInput('Ava', 'bad-email', 'Hello there')") == "Please enter a valid email address."
    assert (
        run_php("validateContactInput('Ava', 'ava@example.com', str_repeat('x', 1001))")
        == "Please enter a message under 1000 characters."
    )
