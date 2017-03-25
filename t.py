from pysqlite2 import dbapi2 as DB

db = DB.connect('t.db')
c = db.cursor()
c.executescript(open('init.sql').read())
