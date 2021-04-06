Feature: kindergarten management
  This feature file will verify kindergarten create/update/delete to verify we have only the relevant kindergarten
  without duplication and with the relevant data only.
  Will not verify the excel inputs

  Scenario: Create new kindergarten
    Given you are the admin
    When you get an email to create new kindergarten
    And you verify you get excel file template
    And you reply with updated excel file
    Then lambda function will get the relevant emails
    And new record will be created in DB for each kindergarten
    And will send emails to all kindergarten teachers
    And new record will be created for each kindergarten teacher


  Scenario: Create new kindergarten with wrong kindergarten teacher email
    Given you are the admin
    When you get an email to create new kindergarten
    And you verify you get excel file template
    And you reply with updated excel file
    Then lambda function will get the relevant emails
    And new record will be created in DB for each kindergarten
    And will not fail because of the wrong kindergarten teacher email
    And will send emails to all kindergarten teachers
    And new record will be created for each kindergarten teacher


  Scenario: Update kindergarten teacher in exist kindergarten
    Given you are the admin
    When you reply to the email with updated kindergarten teacher by excel file
    Then the record in DB will update with new teacher details


  Scenario: Delete kindergarten
    Given you are the admin
    When you reply to the email without specific kindergarten
    Then the record in DB will not contain with deleted kindergarten
    And all the relevant records about the kindergarten teachers still exist (Question: need to verify this - only in the future


  Scenario: Support two kindergarten teacher with the same name and different kindergarten ID
    Given you are the admin
    When you reply to the email with same names and different id for kindergarten teacher with different kindergarten id
    Then new record will be created in DB for each kindergarten teacher


  Scenario: Not support two kindergarten with the same id
    Given you are the admin
    When you reply to the email with same names for kindergarten id
    Then you will get failure since the DB will failed to create one of the records


  Scenario: Email reply after expiration time
    Given you are the admin
    When you reply to the email after expiration time
    Then no records will insert to the DB




