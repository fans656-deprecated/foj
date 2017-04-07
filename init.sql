drop table if exists problem;
create table problem (
    title text,
    url_name text,
    desc text,
    n_acceptions integer default 0,
    n_submissions integer default 0
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

drop table if exists comment_tag;
create table comment_tag (
    cid integer references comment(rowid),
    tag text,
    primary key (cid, tag)
);

drop table if exists snippet;
create table snippet (
    pid integer references problem(rowid),
    lang text,
    code text
);

drop table if exists testcode;
create table testcode (
    pid integer references problem(rowid),
    lang text,
    lang_name text,
    code text,
    primary key (pid, lang)
);

drop table if exists submission;
create table submission (
    pid integer references problem(rowid),
    lang text,
    code text,
    ctime datetime,
    state text,
    info text
);

drop table if exists user;
create table user (
    name text,
    password text,
    register_time datetime,
    last_login datetime,
    state text
);

/***************************************************/

insert into problem (title, url_name, desc) values (
    "A + B",
    "a-b",
    "Given two integers, return their sum."
    || char(10) ||
    "Sample Input: 2 3"
    || char(10) ||
    "Sample Output: 5"
);
insert into snippet (pid, lang, code) values (
    1,
    "python2",
    "def a_plus_b(a, b):"||char(10)||"    pass"
);
insert into snippet (pid, lang, code) values (
    1,
    "cpp",
    "int a_plus_b(int a, int b) {"||char(10)||"    ;"||char(10)||"}"
);
insert into testcode (pid, lang, code) values (
    1,
    "python2",
    "a_plus_b(3, 2)"
);
insert into testcode (pid, lang, code) values (
    1,
    "cpp",
    "a_plus_b(3, 2);"
);
insert into problem (title, url_name, desc) values (
    "Show tree",
    "show-tree",
    "Given a root node, output its indented tree structure."
);
