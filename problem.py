from db import get_db, get_cursor, get_db_cursor
from lang import Lang

import re
import json

class Problem(object):

    langs = [Lang(id) for id in Lang.ids]

    def __init__(self, pid, title='',
                 n_acceptions=0,
                 n_submissions=0,
                 load=False, new=False):
        self.pid = pid
        self.title = title
        self.tags = []
        self.url_name = title_to_urlname(title)
        self.desc = ''
        self.n_acceptions = n_acceptions
        self.n_submissions = n_submissions
        self.snippets = {}
        self.testcodes = {}
        self.last_submission_codes = {}

        if not load:
            self.dirty = True
        else:
            self.load()
        if new:
            self.new()

    @property
    def tags_repr(self):
        return u','.join(self.tags)

    def load(self):
        c = get_cursor()
        # title & description
        c.execute('select title, desc from problem where rowid = ?',
                  (self.pid,))
        self.title, self.desc = c.fetchone()
        # tags
        c.execute('select tag from tag where pid = ?', (self.pid,))
        self.tags = [v[0] for v in c]
        # testcode
        c.execute('select lang, code from testcode where pid = ?',
                  (self.pid,))
        self.testcodes = dict(list(c))
        # snippet
        c.execute('select lang, code from snippet where pid = ?',
                  (self.pid,))
        self.snippets = dict(list(c))
        # last submission code
        self.last_submission_codes = {}
        for lang in self.snippets:
            code = self.last_submission_code(lang)
            self.last_submission_codes[lang] = code
        # submissions
        c.execute('select count(*) from submission where pid=?', (self.pid,))
        self.n_submissions = c.fetchone()[0]
        c.execute('select count(*) from submission where pid=? and state=?',
                  (self.pid, 'accepted'))
        self.n_acceptions = c.fetchone()[0]
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
        pid = data.get('pid', None)
        title = data.get('title', '')
        tags = data.get('tags', '')
        desc = data.get('desc', '')
        snippets = data.get('snippets', [])
        testcodes = data.get('testcodes', [])
        # validate
        if pid is None:
            raise ValueError('Invalid Problem ID')
        if not title:
            raise ValueError('Title can not be empty')
        # check if title already used
        if self.title != title:
            c = get_cursor()
            c.execute('select rowid from problem where title=?', (title,))
            r = c.fetchone()
            if r:
                raise ValueError(
                    'Title "{}" already used by problem {}'.format(
                        title, r[0]))
        # change
        if self.pid is None:
            self.pid = pid
        self.title = title
        self.tags = filter(bool, [s.strip() for s in tags.split(',')])
        self.desc = desc
        self.url_name = title_to_urlname(self.title)
        self.snippets = {v['lang']: v['code'] for v in snippets}
        self.testcodes = {v['lang']: v['code'] for v in testcodes}
        # check if is new
        db, c = get_db_cursor()
        c.execute('select count(*) from problem where rowid=?', (self.pid,))
        is_new_problem = c.fetchone()[0] == 0
        if is_new_problem:
            c.execute('insert into problem (rowid, title, url_name, desc) '
                      + 'values (?,?,?,?)', (
                          self.pid, self.title, self.url_name, self.desc))
            for lang, code in self.snippets.items():
                c.execute('insert into snippet (pid, lang, code) '
                          + 'values (?,?,?)', (self.pid, lang, code))
            for lang, code in self.testcodes.items():
                c.execute('insert into testcode (pid, lang, code) '
                          + 'values (?,?,?)', (self.pid, lang, code))
            for tag in self.tags:
                c.execute('insert into tag (pid, tag) values (?, ?)',
                          (self.pid, tag))
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
            # update tags
            c.execute('select tag from tag where pid = ?', (self.pid,))
            pre = set(v[0] for v in c)
            cur = set(self.tags)
            print pre, cur
            # remove tag
            for tag in pre - cur:
                print 'remove tag', tag
                c.execute('delete from tag where pid = ? and tag = ?',
                          (self.pid, tag))
            # add tag
            for tag in cur - pre:
                print 'add tag', tag
                c.execute('insert into tag (pid, tag) values (?, ?)',
                          (self.pid, tag))
        db.commit()
        self.backup()

    def backup(self):
        d = {
            'pid': self.pid,
            'title': self.title,
            'tags': self.tags,
            'url_name': self.url_name,
            'desc': self.desc,
            'n_acceptions': 0,
            'n_submissions': 0,
            'snippets': self.snippets,
            'testcodes': self.testcodes,
            'last_submission_codes': self.last_submission_codes,
        }
        with open('problems/{}.json'.format(self.pid), 'w') as f:
            f.write(json.dumps(d, indent=4))

def get_problems(order_by='id'):
    c = get_cursor()
    if order_by == 'id':
        c.execute('select rowid, title, n_acceptions, n_submissions ' +
                  'from problem order by rowid')
    else:
        raise Exception('get_problems order by "{}" not supported', order_by)
    return [Problem(pid, title,
                    n_acceptions=n_acceptions,
                    n_submissions=n_submissions)
            for pid, title, n_acceptions, n_submissions in c]

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
