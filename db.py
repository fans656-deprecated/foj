try:
    from pysqlite2 import dbapi2 as DB
except ImportError:
    import sqlite3 as DB
from flask import g

import os
import json

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
    dirpath = './problems/'
    for fname in os.listdir(dirpath):
        fpath = os.path.join(dirpath, fname)
        with open(fpath) as f:
            d = json.load(f)
        pid = d['pid']
        c.execute('insert into problem (rowid, title, url_name, desc, ' +
                  'n_acceptions, n_submissions) values (?,?,?,?,?,?)',
                  (pid, d['title'], d['url_name'], d['desc'],
                   d['n_acceptions'], d['n_submissions']))
        for lang, code in d['snippets'].items():
            c.execute('insert into snippet (pid, lang, code) values (?,?,?)',
                      (pid, lang, code))
        for lang, code in d['testcodes'].items():
            c.execute('insert into testcode (pid, lang, code) values (?,?,?)',
                      (pid, lang, code))
        for tag in d['tags']:
            c.execute('insert into tag (pid, tag) values (?,?)',
                      (pid, tag))
    db.commit()

if __name__ == '__main__':
    db = DB.connect(DB_NAME)
    init()
    r = db.execute('select title from problem')
    print list(r)
