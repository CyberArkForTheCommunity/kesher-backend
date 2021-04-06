USE Kesher;

DELIMITER // ;


DROP PROCEDURE IF EXISTS insert_user;

Create PROCEDURE  insert_user( IN first_name VARCHAR(255), 
			       IN last_name VARCHAR(255),
			       IN email_address VARCHAR(255),
                               IN id_number  VARCHAR(255),
			       IN user_type ENUM('admin','kinder-gardener','parent', 'admin_and_kindergardener'), 
                               IN is_deleted BOOL)
BEGIN
	insert into users(first_name, last_name, email_address, id_number, user_type, is_deleted) values (first_name, last_name, email_address, id_number, user_type, is_deleted);
END;

// ;

DELIMITER // ;


DROP PROCEDURE IF EXISTS get_user_by_id;

Create PROCEDURE  get_user_by_id(
                                  IN id_number_input  VARCHAR(255))
BEGIN
	SELECT * FROM users WHERE id_number = id_number_input;
END;

// ;


DELIMITER // ;

DROP PROCEDURE IF EXISTS insert_garten_members;

Create PROCEDURE insert_garten_members ( IN kindergarten_id INT, 
										 IN kindergarten_name VARCHAR(255),
										 IN kindergardener_first_name VARCHAR(255),
										 IN kindergardener_last_name VARCHAR(255),
                                         IN kindergardener_email_address VARCHAR(255),
                                         IN kindergardener_id VARCHAR(255),
										 IN is_deleted BOOL)
BEGIN
    insert into kinder_gartens(kindergarten_id,kindergarten_name) values (kindergarten_id,kindergarten_name);
    insert into users(first_name, last_name, email_address, id_number, user_type, is_deleted) values (kindergardener_first_name, kindergardener_last_name, kindergardener_email_address, kindergardener_id, 'kinder-gardener', is_deleted);
    insert into kindergarten_staff_mapping(kindergarten_id, user_id) values (kindergarten_id, (select id from users where id_number = kindergardener_id));
    
END;

// ;


DELIMITER // ;

DROP PROCEDURE IF EXISTS  insert_child_parents;

Create PROCEDURE insert_child_parents ( IN kindergarten_id INT,
										IN child_id VARCHAR(255),
										IN child_first_name VARCHAR(255),
										IN child_last_name VARCHAR(255),
										IN child_birth_date DATE,
										IN parent_a_first_name VARCHAR(255),
										IN parent_a_last_name VARCHAR(255),
                                        IN parent_a_email_address VARCHAR(255),
                                        IN parent_a_id VARCHAR(255),
                                        IN parent_b_first_name VARCHAR(255),
										IN parent_b_last_name VARCHAR(255),
                                        IN parent_b_email_address VARCHAR(255),
										IN parent_b_id VARCHAR(255),
										IN is_deleted BOOL)
BEGIN
    insert into children(kindergarten_id, child_id,child_first_name,child_last_name, child_birth_date, is_deleted) values (kindergarten_id, child_id,child_first_name, child_last_name, child_birth_date, is_deleted);
    insert into users(first_name, last_name, email_address, id_number, user_type, is_deleted) values (parent_a_first_name, parent_a_last_name, parent_a_email_address, parent_a_id, 'parent', is_deleted);
    insert into users(first_name, last_name, email_address, id_number, user_type, is_deleted) values (parent_b_first_name, parent_b_last_name, parent_b_email_address, parent_b_id, 'parent', is_deleted);
    insert into parents_children_mapping(child_id, parent_email) values (child_id, parent_a_email_address);
    insert into parents_children_mapping(child_id, parent_email) values (child_id, parent_b_email_address);
END;

// ;

DELIMITER // ;

DROP PROCEDURE IF EXISTS insert_daily_report;

Create PROCEDURE insert_daily_report(
		  IN sender_email VARCHAR(255),
		  IN child_id_input VARCHAR(255),
          IN category_id_input INT,
          IN subcategory_id_input INT,
          IN report_value_input VARCHAR(255))
BEGIN
DECLARE sender_id_input VARCHAR(255);
SET sender_id_input = (SELECT id FROM users AS u WHERE email_address = sender_email LIMIT 1);
INSERT INTO daily_report(sender_id, child_id, report_date, category_id, subcategory_id, report_value)
VALUES(sender_id_input, child_id_input, NOW(), category_id_input, subcategory_id_input, report_value_input);
END;


// ;

DELIMITER // ;

DROP PROCEDURE IF EXISTS get_daily_reports_per_child_id;
 
Create PROCEDURE get_daily_reports_per_child_id(
                                  IN child_id_input VARCHAR(255))
BEGIN
SELECT * FROM daily_report AS dr
WHERE dr.child_id = child_id_input;
END;

// ;

DELIMITER // ;

DROP PROCEDURE IF EXISTS get_categories_and_subcategories;

Create PROCEDURE get_categories_and_subcategories()
BEGIN
SELECT cat.record_id as category_id, sub.record_id as sub_category_id, cat.category_name, sub.subcategory_name
FROM report_categories AS cat
JOIN report_subcategories AS sub
ON cat.record_id = sub.category_id;
END;

// ;
