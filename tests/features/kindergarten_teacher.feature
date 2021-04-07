Feature: kindergarten teacher
  This feature file will verify kindergarten teacher abilities by adding/update/removing user via excel file.
  Not all the inputs verified.
  In addition we will verify kindergarten screens which relevant to the specific kindergarten id

  Scenario: Get the into the application
    Given you are the kindergarten teacher
    When the kindergarten teacher get into the application with right authentication
    Then the kindergarten teacher will get into specific screen with the right kindergarten id


  Scenario: Failed to authenticate to the system
    Given you are the kindergarten teacher
    When the kindergarten teacher get into the application with wrong authentication
    Then the kindergarten teacher will get specific error on authentication


  Scenario: Create list of children on specific kindergarten
    Given you are the kindergarten teacher
    And you get an email from the admin with template excel file
    When you reply to email with updated excel which contain all the children with kindergarten id
    Then new records will be created in DB for each children


  Scenario: Create list of children with wrong kindergarten id
    Given you are the kindergarten teacher
    And you get an email from the admin with template excel file
    When you reply to email with updated excel which contain all the children with wrong kindergarten id
    Then new records will be created in DB for each children


  Scenario: Create list of children with duplicate name of one of the children
    Given you are the kindergarten teacher
    And you get an email from the admin with template excel file
    When you reply to email with updated excel which contain 2 children with the same name
    Then new records will be created in DB for each children (the unique id is the children id)


  Scenario: Create list of children with duplicate id for two children
    Given you are the kindergarten teacher
    And you get an email from the admin with template excel file
    When you reply to email with updated excel which contain 2 children id with the same name
    Then only the first name will be created and we will get an error in db


  Scenario: Verify attendance of all children
    Given you are the kindergarten teacher
    When you press on attendance button
    Then you will get/see the list of all the children in your kindergarten


  Scenario Outline: Get into kindergarten screens
    Given you are the kindergarten teacher
    And the kindergarten teacher get into the application with right authentication
    When you get into the <screen>
    Then the kindergarten teacher will see the relevant screen

    Examples:
      | screen              | subscreen            |
      | meals               | breakfast            |
      | meals               | fruit                |
      | meals               | launch               |
      | meals               | minha                |
      | activities          | meetings             |
      | activities          | table games          |
      | activities          | jamboree             |
      | activities          | play around          |
      | activities          | arts and crafts      |
      | activities          | daily skills         |
      | required equipment  | sheet                |
      | required equipment  | clean clothes        |
      | required equipment  | diapers              |
      | required equipment  | fresh wipes          |
      | required equipment  | other                |
      | medical care        | physiotherapy        |
      | medical care        | speech therapy       |
      | medical care        | occupational therapy |
      | medical care        | emotional therapy    |


  Scenario: Delete specific child, assume the parent have more than one child on the system
    Given you are the kindergarten teacher
    And the parent have more than one child
    When kindergarten teacher remove one child from parents
    Then the child DB record removed
    And the kindergartens parents exist with specific children only


  Scenario: Delete specific child, assume the parent have one child on the system
    Given you are the kindergarten teacher
    And the parent have more one child
    When kindergarten teacher remove one child from parents
    Then the child DB record removed
    And the kindergartens parents removed as well