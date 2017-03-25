import config
from run import run_submission
from db import get_db, get_cursor, get_db_cursor

from datetime import datetime

class Problem(object):

    def __init__(self, pid, title='', desc='', testcode=''):
        self.title = title
        self.url_name = title_to_url_name(title)
        self.desc = desc
        self._testcode = testcode
        self.pid = pid
        self.python_code = ''
        self.cpp_code = ''
        self.dirty = False

    @property
    def testcode(self):
        if self.dirty:
            self.dirty = False
            c = get_cursor()
            testcode = c.execute('select testcode from problems where id = ?',
                                 (self.pid,)).fetchone()[0]
            self.testcode = testcode
        return self._testcode

    @testcode.setter
    def testcode(self, v):
        self._testcode = v

    def as_tuple(self):
        return (self.pid, self.title, self.url_name, self.desc, self.testcode)

    @staticmethod
    def from_id(pid):
        c = get_cursor()
        c.execute('select title, desc from problems where id = ?',
                  (pid,))
        title, desc = c.fetchone()
        p = Problem(pid, title, desc=desc)
        p.dirty = True
        return p

    def insert_into_db(self):
        db, c = get_db_cursor()
        c.execute('insert into problems values (?,?,?,?,?)',
                  (self.pid, self.title, self.url_name, self.desc,
                   self.testcode))
        c.execute('insert into problem values (?,?,?)',
                  (self.pid, self.python_code, self.cpp_code))
        db.commit()

    def submit(self, lang, code):
        if lang not in config.langs:
            raise RuntimeError('unknown language')
        db, c = get_db_cursor()
        c.execute('''
insert into submissions (pid, lang, code, timestamp, state) values
(?,?,?,?,?)
''', (self.pid, lang, code, datetime.now(), 'Pending'))
        c.execute('select last_insert_rowid() from submissions')
        sid = c.fetchone()[0]
        db.commit()
        run_submission(sid=sid, problem=self, lang=lang, code=code)
        return sid

def title_to_url_name(s):
    return s.lower().replace(' ', '-')

def get_problems():
    res = get_cursor().execute('select id, title from problems')
    for (pid, title,) in res:
        problem = Problem(pid, title)
        yield problem

def get_problem(url_name):
    c = get_cursor()
    c.execute('select id from problems where url_name = ?', (url_name,))
    return Problem.from_id(c.fetchone()[0])

def get_new_problem_id():
    return get_cur_problem_id() + 1

def get_cur_problem_id():
    c = get_cursor()
    c.execute('select count(*) from problems')
    pid = c.fetchone()[0]
    return pid

def db_init():
    db, c = get_db_cursor()
    c.execute('drop table if exists problems')
    c.execute('''
create table problems (
    id int primary key,
    title text,
    url_name text,
    desc text,
    testcode text
)
              ''')
    c.execute('drop table if exists problem')
    c.execute('''
create table problem (
    id int references problems(id),
    python_code text,
    cpp_code text
)
              ''')
    c.execute('drop table if exists submissions')
    c.execute('''
create table submissions (
    sid integer primary key autoincrement,
    pid int references problems(id),
    lang text,
    code text,
    timestamp datetime,
    state text
)
              ''')
    p = Problem(1, 'A plus B',
                desc='''
Given two int, return their sum.

Input eg:
    2 3

Output eg:
    5
                ''')
    p.python_code = '''
def sum_of_two(a, b):
    pass
    '''
    p.cpp_code = '''
int sum_of_two(int a, int b) {

}
    '''
    p.insert_into_db()

    p = Problem(2, 'Show root', desc='''
Give a tree node, return its value.
                ''')
    p.python_code = '''
# class Node:
#     def __init__(self, val):
#         self.val = val
#         self.left = None
#         self.right = None

def show(root):
    return root.val
    '''
    p.testcode = '''
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

root = Node(656)
print show(root)
    '''
    p.insert_into_db()
    db.commit()

if __name__ == '__main__':
    pass
    db_init()
    print list(get_cursor().execute('select * from problems'))
