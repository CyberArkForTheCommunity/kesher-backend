Feature: kindergarten parent
  This feature file will verify kindergarten screens which relevant to the specific kindergarten parents related to
  their children

  Scenario: Get the relevant data for specific child, assume the parent have only one child on the system
    Given you are the kindergarten parent with one child in the system
    When the parent get into the application with right authentication
    Then the parent will get into specific screen of the relevant child


  Scenario: Failed to authenticate to the system
    Given you are the kindergarten parent with one child in the system
    When the parent get into the application with wrong authentication
    Then the parent will get specific error on authentication


  Scenario: Get the relevant data for specific child, assume the parent have more than one child on the system
    Given you are the kindergarten parent with more than one child in the system
    When the parent get into the application with right authentication
    And will see a list of all of her/his children
    And the parent will choose specific child from list
    Then the parent will get into specific screen of the relevant child


  Scenario Outline: Get into parents screens
    Given you are the kindergarten parent with at least one child in the system
    And the parent get into the application with right authentication
    When you get into the <screen>
    Then the parent will see the relevant screen

    Examples:
      |screen       |
      |covid19      |
      |daily status |
      |calendar     |
      |albums       |


  Scenario: Get into daily status screens and get all data
    Given you are the kindergarten parent with at least one child in the system
    And the parent get into the application with right authentication
    And get into daily status screen
    When the parent scroll up in the screen
    Then the parent will get all the relevant data of the last month
