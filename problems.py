import config

from pysqlite2 import dbapi2 as db

class Problem(object):

    def __init__(self, pid, title, desc=None, testcases=None):
        self.title = title
        self.url_name = title_to_url_name(title)
        self.desc = desc
        self.testcases = testcases
        self.pid = pid

    def as_tuple(self):
        return (self.pid, self.title, self.url_name, self.desc, self.testcases)

    @staticmethod
    def from_id(pid):
        c = get_cursor()
        c.execute('select title, desc from problems where id = ?',
                  (pid,))
        title, desc = c.fetchone()
        return Problem(pid, title, desc=desc)

    def insert_into_db(self):
        db, c = get_db_cursor()
        c.execute('insert into problems values (?,?,?,?,?)',
                  (self.pid, self.title, self.url_name, self.desc,
                   self.testcases))
        c.execute('insert into problem values (?,?,?)',
                  (self.pid, self.python_code, self.cpp_code))
        db.commit()

    def submit(self, lang, code):
        if lang not in config.langs:
            raise RuntimeError('unknown language')
        print '=' * 60
        print 'Submit code'
        print code
        print '=' * 60
        return None

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
    testcases text
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
    sid int primary key,
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
    db.commit()

def get_db():
    return db.connect('problems.db')

def get_cursor():
    return get_db().cursor()

def get_db_cursor():
    db = get_db()
    return db, db.cursor()

if __name__ == '__main__':
    db_init()
    for p in get_problems():
        print p.title, p.url_name, p.pid
