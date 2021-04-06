CREATE DATABASE IF NOT EXISTS Kesher;
USE Kesher;


-- ---------------------------------------------------------
-- ---------------------------DELETE TABLES ----------------
-- ---------------------------------------------------------
-- Need to run this section first in case you want to recreate the tables --
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS daily_report;
DROP TABLE IF EXISTS report_subcategories;
DROP TABLE IF EXISTS report_categories;
DROP TABLE IF EXISTS parents_children_mapping;
DROP TABLE IF EXISTS kindergarten_staff_mapping;
DROP TABLE IF EXISTS children;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS kinder_gartens;

-- ---------------------------------------------------------
-- --------------------- CREATE USERS table ----------------
-- ---------------------------------------------------------
-- |id                      | user_type                                             |  first_name      | last_name      | email_address      | id_number | is_deleted                 |
-- |an auto generated index | admin/kinder-gardener/parent/admin_and_kindergardener |  user first name | user last name | user email address | user id   | true if need to be deleted |
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_type ENUM('admin','kinder-gardener','parent', 'admin_and_kindergardener') NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name  VARCHAR(255) NOT NULL,
    email_address  VARCHAR(255) NOT NULL,
    id_number VARCHAR(255) NOT NULL,
    is_deleted BOOL NOT NULL,
    UNIQUE(email_address));
 
 -- CREATE fake admin user ---
 INSERT INTO users(user_type, first_name, last_name, email_address, id_number, is_deleted) 
 VALUES('admin','Israel', 'Israeli','israel_i@gmail.com','000000000',FALSE);
 
-- ---------------------------------------------------------
-- ----- CREATE kindergarten_staff_mapping table -----------
-- --------------------------------------------------------- 
-- | record_id                  | kindergarten_id                                                | user_id                                       | 
-- | an auto generated index    | id number of the kindergarten as signed in the welfare office  | the auto generated index from the users table |
CREATE TABLE IF NOT EXISTS kindergarten_staff_mapping (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    kindergarten_id INT,
    user_id INT,
    UNIQUE (kindergarten_id),
    FOREIGN KEY (user_id) REFERENCES users(id));

-- ---------------------------------------------------------
-- ------------ CREATE kinder_gartens table ----------------
-- --------------------------------------------------------- 
-- | record_id                  |  kindergarten_id                                               | kindergarten_name                 |
-- | an auto generated index    | id number of the kindergarten as signed in the welfare office  | the name of the kindergarten      |
CREATE TABLE IF NOT EXISTS kinder_gartens (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    kindergarten_id INT NOT NULL,
    kindergarten_name VARCHAR(255) NOT NULL,
    UNIQUE (kindergarten_id));
    
    
-- ---------------------------------------------------------
-- ---------------- CREATE children table ------------------
-- ---------------------------------------------------------
-- | record_id                  |  kindergarten_id                                | child_id       | child_first_name| child_last_name | child_birth_date| is_deleted                |
-- | an auto generated index    | the kindergarten_id from kinder_gartens table   | id of the child| first name      | last name       | date of birth   |true if need to be deleted |
CREATE TABLE IF NOT EXISTS children (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    kindergarten_id INT NOT NULL,
    child_id VARCHAR(255) NOT NULL,
    child_first_name  VARCHAR(255) NOT NULL,
    child_last_name  VARCHAR(255) NOT NULL,
    child_birth_date DATE NOT NULL,
    is_deleted BOOL,
    UNIQUE(child_id),
    FOREIGN KEY (kindergarten_id) REFERENCES kinder_gartens(kindergarten_id));
    

-- ---------------------------------------------------------
-- ------ CREATE parents_children_mapping table ------------
-- --------------------------------------------------------- 
-- | record_id                  | child_id                              | parent_email                            |
-- | an auto generated index    | the child_id from the children table  | the email_address from the users table  |
CREATE TABLE IF NOT EXISTS parents_children_mapping (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id VARCHAR(255) NOT NULL,
    parent_email  VARCHAR(255) NOT NULL,
    FOREIGN KEY (parent_email) REFERENCES users(email_address),
    FOREIGN KEY (child_id) REFERENCES children(child_id));
    
-- ---------------------------------------------------------
-- ---------------- CREATE attendance table ----------------
-- --------------------------------------------------------- 
-- | record_id                  | child_id                              | arrival_date                       |  arrival_time                   |
-- | an auto generated index    | the child_id from the children table  | the date when the child arrived    | the time when the child arrived |
CREATE TABLE IF NOT EXISTS attendance (
record_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
child_id VARCHAR(255) NOT NULL,
FOREIGN KEY (child_id) REFERENCES children(child_id),
arrival_date DATE NOT NULL,
arrival_time TIME NOT NULL);


-- ---------------------------------------------------------
-- ------------- CREATE report_categories table ------------
-- --------------------------------------------------------- 
-- | record_id                  | category_name                                            |
-- | an auto generated index    | 'meals'/'activities'/'required equipment'/'medical care' |
CREATE TABLE IF NOT EXISTS report_categories (
record_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
category_name ENUM('meals', 'activities', 'required equipment', 'medical care') NOT NULL,
CONSTRAINT category_name_constraint UNIQUE (category_name));


INSERT INTO report_categories (category_name) VALUES ('meals'),
																								('activities'),
                                                                                                ('required equipment'),
                                                                                                ('medical care');
-- ---------------------------------------------------------
-- ----------- CREATE report_subcategories table -----------
-- --------------------------------------------------------- 
-- | record_id                  | category_id                                               | subcategory_name                                                     |
-- | an auto generated index    | the record_id in report_categories (meals)                | breakfast/fruit/lunch/Minha                                          |
-- |                            | 2 (activities)                                            | table games/jamboree/play around/ arts and crafts/ daily skills      |
-- |                            | 3 (required equipment)                                    | sheets/clothes/diapers/ fresh wipess/ others                         |
-- |                            | 4 (medical care)                                          | physiotherapy/speech therapy/occupational therapy/ emotional therapy |                    |

CREATE TABLE IF NOT EXISTS report_subcategories (
category_id INT NOT NULL,
FOREIGN KEY (category_id) REFERENCES report_categories(record_id),
subcategory_name VARCHAR(255) NOT NULL,
record_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
CONSTRAINT subcategory_name_constraint UNIQUE (subcategory_name));



INSERT INTO report_subcategories (category_id, subcategory_name) 
VALUES (1,'breakfast'), (1,'fruit'), (1, 'lunch'), (1, 'Minha'),
			   (2,'table games'), (2,'jamboree'), (2, 'play around'), (2, 'arts and crafts' ), (2, 'daily skills' ),
               (3,'sheets'), (3,'clothes'), (3, 'diapers'), (3, 'fresh wipes' ), (3, 'other' ),
               (4,'physiotherapy'), (4, 'speech therapy'), (4, 'occupational therapy'), (4, 'emotional therapy');
               
               
-- ---------------------------------------------------------
-- --------------- CREATE daily_report table ---------------
-- ---------------------------------------------------------   
-- | record_id                  | sender_id                                                  | child_id                              | report_date    | category_id                           | subcategory_id                            | report_value                             |
-- | an auto generated index    | the generated id of who that reported from the users table | the child_id from the children table  | reported date  | record_id from report_categories table| record_id from report_subcategories table | free text that describes the subcategory |
-- | 1                          | 3                          | '362388142'                           | 04-05-2021     | 1                                     | 2                                         | 'banana'                                 |
CREATE TABLE IF NOT EXISTS daily_report (
record_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
sender_id INT NOT NULL, 
FOREIGN KEY (sender_id) REFERENCES users(id),
child_id VARCHAR(255) NOT NULL,
FOREIGN KEY (child_id) REFERENCES children(child_id),
report_date DATETIME NOT NULL,
category_id INT NOT NULL,
FOREIGN KEY (category_id) REFERENCES report_categories(record_id),
subcategory_id INT NOT NULL,
FOREIGN KEY (subcategory_id) REFERENCES report_subcategories(record_id),
report_value VARCHAR(255));
