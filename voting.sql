use survey;
create table voting(
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id varchar(1000),
    question varchar(1000),
    yes int,
    no int
);


