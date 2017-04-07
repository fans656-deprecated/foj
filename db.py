from pysqlite2 import dbapi2 as DB
from flask import g

DB_NAME = 'data.db'

def get_db():
    try:
        if not hasattr(g, 'db'):
            g.db = DB.connect(DB_NAME)
        return g.db
    except RuntimeError:
        return DB.connect(DB_NAME)

def get_cursor():
    return get_db().cursor()

def get_db_cursor():
    db = get_db()
    return db, db.cursor()

def connect():
    return DB.connect(DB_NAME)

def init():
    db = DB.connect(DB_NAME)
    db.executescript(open('init.sql').read())
    c = db.cursor()
    c.execute('update testcode set code = ? where pid = ? and lang = ?',
              ('''\
for x, y in (
        (2, 3),
        (0, -1),
):
    res = a_plus_b(x, y)
    expect_res = x + y
    if res != expect_res:
        raise WrongAnswer('Input {}, Expect {}, Got {}'.format(
            (x, y), expect_res, res
        ))
               ''', 1, 'python2'))
    db.commit()

if __name__ == '__main__':
    db = DB.connect(DB_NAME)
    init()
    r = db.execute('select title from problem')
    print list(r)
