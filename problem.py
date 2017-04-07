from db import get_db, get_cursor, get_db_cursor

import re
from collections import OrderedDict

class Lang(object):

    id2name = OrderedDict([
        ('python2', 'Python 2.7'),
        ('cpp', 'C++ 11'),
    ])
    ids = id2name.keys()

    def __init__(self, id):
        self.id = id
        self.name = Lang.id2name[id]

class Problem(object):

    langs = [Lang(id) for id in Lang.ids]

    def __init__(self, pid, title='', load=False, new=False):
        self.pid = pid
        self.title = title
        self.url_name = title_to_urlname(title)
        if not load:
            self.dirty = True
        else:
            self.load()
        if new:
            self.new()

    def load(self):
        c = get_cursor()
        # title & description
        c.execute('select title, desc from problem where rowid = ?',
                  (self.pid,))
        self.title, self.desc = c.fetchone()
        # testcode
        c.execute('select lang, code from testcode where pid = ?',
                  (self.pid,))
        self.testcodes = dict(list(c))
        # snippet
        c.execute('select lang, code from snippet where pid = ?',
                  (self.pid,))
        self.snippets = dict(list(c))
        self.last_submission_codes = {}
        # use last submission as snippet if exists
        for lang in self.snippets:
            code = self.last_submission_code(lang)
            self.last_submission_codes[lang] = code
        # loaded
        self.dirty = False

    def last_submission_code(self, lang):
        c = get_cursor()
        c.execute('select code from submission ' +
                  'where pid = ? and lang = ? ' +
                  'order by ctime desc limit 1',
                  (self.pid, lang))
        r = c.fetchone()
        if r is not None:
            return r[0]
        else:
            return ''

    def new(self):
        self.testcodes = {lang: '' for lang in self.langs}
        self.snippets = {lang: '' for lang in self.langs}

    def submit(self, data):
        # validate
        if not data['title']:
            raise ValueError('Title can not be empty')
        if self.title != data['title']:
            c = get_cursor()
            c.execute('select rowid from problem where title=?',
                      (data['title'],))
            r = c.fetchone()
            if r:
                raise ValueError('Title "{}" already used by problem {}'.format(
                    data['title'], r[0]))
        # change
        if self.pid is None:
            self.pid = data['pid']
        self.title = data['title']
        self.desc = data['desc']
        self.url_name = title_to_urlname(self.title)
        self.snippets = {v['lang']: v['code'] for v in data['snippets']}
        self.testcodes = {v['lang']: v['code'] for v in data['testcodes']}
        # check if is new
        db, c = get_db_cursor()
        c.execute('select count(*) from problem where rowid=?', (self.pid,))
        is_new_problem = c.fetchone()[0] == 0
        if is_new_problem:
            c.execute('insert into problem (rowid, title, url_name, desc) '
                      + 'values (?,?,?,?)', (
                          self.id, self.title, self.url_name, self.desc))
            for lang, code in self.snippets.items():
                c.execute('insert into snippet (pid, lang, code) '
                          + 'values (?,?,?)', (self.pid, lang, code))
            for lang, code in self.testcodes.items():
                c.execute('insert into testcode (pid, lang, code) '
                          + 'values (?,?,?)', (self.pid, lang, code))
            print 'inserted new problem "{}"'.format(self.title)
        else:
            # update problem
            c.execute('update problem set title=?, url_name=?, desc=?'
                      + 'where rowid=?',
                      (self.title, self.url_name, self.desc, self.pid))
            # update snippet
            for lang, code in self.snippets.items():
                c.execute('update snippet set code=? where pid=? and lang=?',
                          (code, self.pid, lang))
            # update testcode
            for lang, code in self.testcodes.items():
                c.execute('update testcode set code=? where pid=? and lang=?',
                          (code, self.pid, lang))
        db.commit()

def get_problems(order_by='id'):
    c = get_cursor()
    if order_by == 'id':
        c.execute('select rowid, title from problem order by rowid')
    else:
        raise Exception('get_problems order by "{}" not supported', order_by)
    return [Problem(pid, title) for pid, title in c]

def get_problem_by_url_name(url_name):
    c = get_cursor()
    c.execute('select rowid, title from problem where url_name = ?',
              (url_name,))
    r = c.fetchone()
    if not r:
        return None
    return Problem(*r, load=True)

def get_problem_by_pid(pid):
    c = get_cursor()
    c.execute('select rowid, title from problem where rowid = ?', (pid,))
    r = c.fetchone()
    if not r:
        return Problem(None)
    return Problem(*r, load=True)

def get_new_problem():
    c = get_cursor()
    c.execute('select max(rowid) + 1 from problem')
    r = c.fetchone()
    if not r:
        pid = 1
    else:
        pid = r[0]
    return Problem(pid, new=True)

def title_to_urlname(s):
    s = re.sub(r'[^a-zA-Z0-9 ]', '', s)
    s = re.sub(r' +', '-', s)
    return s.lower()

def state2name(state):
    return ' '.join([word.capitalize() for word in state.split()])

if __name__ == '__main__':
    print Lang.id2name.keys()
