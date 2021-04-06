SELECT * from daily_report where child_id = '217345691';

SELECT child_first_name from children where kindergarten_id = 0;

SELECT subcategory_name from report_subcategories where category_id = 3;

INSERT INTO `Kesher`.`attendance`
(`child_id`,
`arrival_date`,
`arrival_time`)
VALUES
('217345691',
 '2021-06-04',
'09:02:30'),
('281045692',
 '2021-06-04',
'08:45:21');
SELECT child_id, arrival_time from attendance;

