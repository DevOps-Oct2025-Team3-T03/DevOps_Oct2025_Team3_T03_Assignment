"""
Step definitions for authentication service BDD tests.
Uses pytest-bdd to connect Gherkin scenarios to Python test code.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import uuid

# Load all scenarios from the feature file
scenarios("../features/auth_service.feature")

# ============================================================================
# FIXTURES - Context Management
# ============================================================================


@pytest.fixture
def context():
    """Shared context between steps in a scenario"""
    return {
        "response": None,
        "temp_user": None,
        "admin_logged_in": False,
        "current_user": None,
    }


# ============================================================================
# GIVEN STEPS - Setup and Preconditions
# ============================================================================


@given("the auth service is running")
def auth_service_running(client, context):
    """Verify the auth service is accessible"""
    context["client"] = client
    # Could add health check here if you have one
    assert client is not None


@given("I am logged in as admin")
def login_as_admin(admin_client, context):
    """Login as admin user using the admin_client fixture"""
    context["client"] = admin_client
    context["admin_logged_in"] = True


@given("a temporary user exists")
def temp_user_exists(temp_user, context):
    """Create a temporary user for testing"""
    context["temp_user"] = temp_user


# ============================================================================
# WHEN STEPS - Actions
# ============================================================================


@when(parsers.parse('I login with username "{username}" and password "{password}"'))
def login_with_credentials(context, username, password):
    """Attempt to login with provided credentials"""
    response = context["client"].post(
        "/login", json={"username": username, "password": password}
    )
    context["response"] = response


@when(
    parsers.parse(
        'I create a user with username "{username}" and password "{password}" and role "{role}"'
    )
)
def create_user(context, username, password, role):
    """Create a new user via admin endpoint"""
    # Generate unique username to avoid conflicts
    unique_username = f"{username}_{uuid.uuid4().hex[:8]}"

    response = context["client"].post(
        "/admin/create_user",
        json={"username": unique_username, "password": password, "role": role},
    )
    context["response"] = response

    # Store for cleanup if successful
    if response.status_code == 200:
        # Get user_id for cleanup
        users_response = context["client"].get("/admin")
        if users_response.status_code == 200:
            users = users_response.get_json()
            user_data = next(
                (u for u in users if u["username"] == unique_username), None
            )
            if user_data:
                context["created_user"] = {
                    "username": unique_username,
                    "user_id": user_data["user_id"],
                }


@when("I request the list of all users")
def request_user_list(context):
    """Request the admin endpoint to get all users"""
    response = context["client"].get("/admin")
    context["response"] = response


@when("I delete the temporary user")
def delete_temp_user(context):
    """Delete the temporary user"""
    user_id = context["temp_user"]["user_id"]
    response = context["client"].post(f"/admin/delete_user/{user_id}")
    context["response"] = response


@when("I logout")
def logout(context):
    """Logout the current user"""
    response = context["client"].get("/logout")
    context["response"] = response
    context["admin_logged_in"] = False


@when("I login as the temporary user")
def login_as_temp_user(context):
    """Login with the temporary user credentials"""
    temp_user = context["temp_user"]
    response = context["client"].post(
        "/login",
        json={"username": temp_user["username"], "password": temp_user["password"]},
    )
    context["response"] = response
    context["current_user"] = temp_user


@when("I try to access the admin user list")
def try_access_admin_list(context):
    """Attempt to access admin endpoint"""
    response = context["client"].get("/admin")
    context["response"] = response


# ============================================================================
# THEN STEPS - Assertions
# ============================================================================


@then(parsers.parse("the response status should be {status:d}"))
def check_response_status(context, status):
    """Verify the HTTP response status code"""
    assert context["response"].status_code == status, (
        f"Expected status {status}, got {context['response'].status_code}. "
        f"Response: {context['response'].get_json()}"
    )


@then("the response should contain a valid session")
def check_valid_session(context):
    """Verify response indicates successful login"""
    data = context["response"].get_json()
    assert data is not None
    # Adjust based on your actual response structure
    # Example: check for session token or success message
    assert context["response"].status_code == 200


@then("the response should contain an error message")
def check_error_message(context):
    """Verify response contains an error"""
    data = context["response"].get_json()
    assert data is not None
    # Adjust based on your actual error response structure
    assert (
        "error" in data or "message" in data or context["response"].status_code >= 400
    )


@then(parsers.parse('the response should contain "{text}"'))
def check_response_contains_text(context, text):
    """Verify response contains specific text"""
    data = context["response"].get_json()
    response_str = str(data).lower()
    assert text.lower() in response_str, f"Expected '{text}' in response, got: {data}"


@then("the response should contain a list of users")
def check_user_list(context):
    """Verify response contains a list of users"""
    data = context["response"].get_json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "User list should not be empty"
    # Check that users have expected fields
    assert "username" in data[0]


@then("the user should no longer exist in the system")
def verify_user_deleted(context):
    """Verify the user has been deleted"""
    # Get current user list
    response = context["client"].get("/admin")
    if response.status_code == 200:
        users = response.get_json()
        deleted_user_id = context["temp_user"]["user_id"]
        # Verify user is not in the list
        assert not any(u["user_id"] == deleted_user_id for u in users), (
            f"User {deleted_user_id} should have been deleted"
        )


# ============================================================================
# CLEANUP HOOKS
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_created_users(context, request):
    """Automatically cleanup any users created during tests"""
    yield

    # Cleanup created user if exists
    if "created_user" in context and context.get("admin_logged_in"):
        try:
            user_id = context["created_user"]["user_id"]
            context["client"].post(f"/admin/delete_user/{user_id}")
        except:
            pass  # Best effort cleanup
