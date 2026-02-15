"""
BDD Step definitions for authentication service tests.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import uuid

# Load all scenarios from the feature file
scenarios("../features/auth_service.feature")

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def context():
    """Shared context between steps in a scenario"""
    return {
        "response": None,
        "temp_user": None,
        "created_user": None,
        "user_to_delete": None,
    }


# ============================================================================
# GIVEN STEPS
# ============================================================================


@given(parsers.parse('I log in as "{role}"'))
def prepare_to_login(role, context):
    """Prepare context for login"""
    context["role"] = role


@given(parsers.parse('I am logged in as "{role}"'))
def login_as_role(client, admin_client, temp_user, role, context):
    """Login based on role"""
    if role == "admin":
        context["client"] = admin_client
    elif role == "user":
        res = client.post(
            "/login",
            json={"username": temp_user["username"], "password": temp_user["password"]},
        )
        assert res.status_code == 200
        context["client"] = client
        context["temp_user"] = temp_user


# ============================================================================
# WHEN STEPS
# ============================================================================


@when("I input a valid username")
def input_username(context):
    """Username step - combined with password"""
    pass


@when("I input a valid password")
def input_password(client, temp_user, context):
    """Actually perform the login"""
    if context.get("role") == "admin":
        res = client.post(
            "/login", json={"username": "admin", "password": "AdminPass123!"}
        )
    else:
        res = client.post(
            "/login",
            json={"username": temp_user["username"], "password": temp_user["password"]},
        )
    context["response"] = res


@when("I choose to log out")
def logout(context):
    """Logout"""
    res = context["client"].get("/logout")
    context["response"] = res


@when("I create a user")
def create_user(context):
    """Create a new user"""
    username = f"test_{uuid.uuid4().hex[:8]}"
    res = context["client"].post(
        "/admin/create_user",
        json={"username": username, "password": "UserPass123!", "role": "user"},
    )
    context["response"] = res
    context["created_user"] = username


@when("I select a user to delete")
def select_user_to_delete(admin_client, context):
    """Create and select user to delete"""
    username = f"del_{uuid.uuid4().hex[:8]}"
    res = admin_client.post(
        "/admin/create_user",
        json={"username": username, "password": "UserPass123!", "role": "user"},
    )

    # Get user_id
    res = admin_client.get("/admin")
    users = res.get_json()
    user_id = next(u["user_id"] for u in users if u["username"] == username)

    # Delete
    res = context["client"].post(f"/admin/delete_user/{user_id}")
    context["response"] = res
    context["user_to_delete"] = user_id


@when(parsers.parse('I visit "{endpoint}"'))
def visit_endpoint(context, endpoint):
    """Visit an endpoint"""
    res = context["client"].get(endpoint)
    context["response"] = res


# ============================================================================
# THEN STEPS
# ============================================================================


@then("I should log in")
def should_login(context):
    """Verify successful login"""
    assert context["response"].status_code == 200
    data = context["response"].get_json()
    assert "username" in data


@then("I should be logged out")
def should_logout(context):
    """Verify successful logout"""
    assert context["response"].status_code == 200
    data = context["response"].get_json()
    assert data["status"] == "logged out"


@then("the user should exist in the system")
def user_exists(context):
    """Verify user was created"""
    assert context["response"].status_code == 200
    data = context["response"].get_json()
    assert data["status"] == "User created"


@then("the user should not exist in the system")
def user_not_exists(context):
    """Verify user was deleted"""
    assert context["response"].status_code == 200
    data = context["response"].get_json()
    assert data["status"] == "User deleted"


@then(parsers.parse("I should receive status code {status:d}"))
def check_status_code(context, status):
    """Verify status code"""
    assert context["response"].status_code == status
