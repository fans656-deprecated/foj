from pysqlite2 import dbapi2 as db

def get_db():
    return db.connect('problems.db')

def get_cursor():
    return get_db().cursor()

def get_db_cursor():
    db = get_db()
    return db, db.cursor()
