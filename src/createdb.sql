create table if not exists results(
    id integer primary key,
    user_id varchar(255) NOT NULL,
    key_word varchar(255) NOT NULL,
    publish_date date NOT NULL,
    finish_date date NOT NULL,
    number_of_purchase varchar(255) NOT NULL,
    subject_of_purchase varchar(500),
    price integer NOT NULL,
    link varchar(255) NOT NULL,
    customer varchar(255),
    location varchar(255)
);