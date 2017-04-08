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
    title text,
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
