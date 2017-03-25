drop table if exists problem;
create table problem (
    title text,
    url_name text,
    desc text
);

drop table if exists tag;
create table tag (
    pid integer references problem(rowid),
    tag text,
    primary key (pid, tag)
);

drop table if exists comment;
create table comment (
    pid integer references problem(rowid),
    comment text,
    ctime datetime,
    mtime datetime
);

drop table if exists testcode;
create table testcode (
    pid integer references problem(rowid),
    lang text,
    testcode text
);

drop table if exists submission;
create table submission (
    pid integer references problem(rowid),
    lang text,
    code text,
    ctime datetime,
    state text
);

drop table if exists user;
create table user (
    name text,
    password text,
    register_time datetime,
    last_login datetime,
    state text
);

insert into problem (title, url_name, desc) values (
    "A + B",
    "A--B",
    "Given two integers, return their sum.\nSample Input: 2 3\nSample Output: 5"
);
