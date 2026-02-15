# TODO: add rename file to test_auth_service_bdd
Feature: Authentication Service

  # Login 

  Scenario: User logs in
    Given I log in as "user"
    When I input a valid username
    And I  input a valid password
    Then I should log in

  Scenario: Admin logs in
    Given I log in as "admin"
    When I input a valid username
    And I  input a valid password
    Then I should log in

  # Log out
  Scenario: User logs out
    Given I am logged in as "user"
    When I choose to log out
    Then I should be logged out

  Scenario: User logs out
    Given I am logged in as "user"
    When I choose to log out
    Then I should be logged out

  # Admin actions
  # Admin creates a new user
  Scenario: Admin creates a new user
    Given I am logged in as "admin"
    When I create a user
    Then the user should exist in the system

  # Admin deletes an existing user
  Scenario: Admin deletes an existing user
    Given I am logged in as "admin"
    When I select a user to delete
    Then the user should not exist in the system

  # Role-based access
  Scenario Outline: Role-base access to admin system
    Given I am logged in as "<role>"
    When I visit "/admin"
    Then I should receive status code <status>

    Examples:
      | role  | status |
      | admin | 200    |
      | user  | 403    |

