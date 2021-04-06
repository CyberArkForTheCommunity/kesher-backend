-- INSERT 'kinder-gardener', parent  into users table
INSERT INTO users(user_type, first_name, last_name, email_address, id_number)
VALUES
('kinder-gardener', 'Jane', 'Doe', 'jane_doe@gmail.com','312654312'),
('kinder-gardener', 'Joan', 'Doe', 'joan_doe@gmail.com','312679318'),
('parent', 'Anne', 'Doe', 'anne_doe@gmail.com','312654304'),
('parent', 'Dan', 'Doe', 'dan_doe@gmail.com', '276890234'),
('parent', 'Yael', 'Shop', 'yael_shop@gmail.com','312654321'),
('parent', 'Guy', 'Shop', 'guy_shop@gmail.com', '276890282'),
('parent', 'Tal', 'Ellen', 'tal_ellen@gmail.com','312654155'),
('parent', 'Gal', 'Ellen', 'gal_ellen@gmail.com', '276890112');

-- INSERT kindergarten_id, kindergarten_name  into kinder_gartens table
INSERT INTO kinder_gartens(kindergarten_id, kindergarten_name)
VALUES
(0,'Nurit'),
(1, 'Savion');


INSERT INTO `Kesher`.`children`
(`kindergarten_id`,
`child_id`,
`child_first_name`,
`child_last_name`,
`is_deleted`)
VALUES
(0,
'217345691',
'Nave',
'Tzuf',
false),
(0,
'281345691',
'Nili',
'Lev',
false),
(1,
'281045692',
'Avi',
'Chai',
false);

INSERT INTO kindergarten_staff_mapping(kindergarten_id, user_id)
VALUES
(0, 3),
(1, 2);


INSERT INTO `Kesher`.`parents_children_mapping`
(`child_id`,
`parent_email`)
VALUES
('217345691',
 'anne_doe@gmail.com'),
 ('217345691',
 'dan_doe@gmail.com'),
 ('281345691',
 'yael_shop@gmail.com'),
 ('281345691',
 'guy_shop@gmail.com'),
 ('281045692',
 'tal_ellen@gmail.com'),
 ('281045692',
 'gal_ellen@gmail.com');
 

INSERT INTO `Kesher`.`attendance`
(`child_id`,
`arrival_date`,
`arrival_time`)
VALUES
('217345691',
 '2021-06-04',
'08:22:17'),
('281045692',
 '2021-06-04',
'08:31:47'),
('281345691',
 '09:01:32',
'TIME: Auto NOW()');


INSERT INTO `Kesher`.`daily_report`
(`sender_id`,
`child_id`,
`report_date`,
`category_id`,
`subcategory_id`,
`report_value`)
VALUES
(1,
'217345691',
'2021-06-04',
2,
8,
'play-doh');

