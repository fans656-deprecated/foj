from db import get_cursor, get_db_cursor
from problem import get_problem_by_pid
from lang import Lang

from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

class Submission(object):

    def __init__(self, pid='', title='', lang='', code='',
                 sid=None, ctime=None, state='pending', info=''):
        self.pid = pid
        self.title = title
        self.lang = lang
        self.ctime = ctime
        self.code = code
        self.testcode = None
        self.code_for_run = None
        self.state = state
        self._info = info
        self._sid = sid

    @staticmethod
    def construct(sid, pid, title, lang, ctime, state):
        s = Submission(sid=sid, pid=pid, title=title, lang=lang,
                       ctime=ctime, state=state)
        return s

    @property
    def info(self):
        if not self._info:
            c = get_cursor()
            c.execute('select info from submission where rowid = ?',
                      (self.sid,))
            self._info = c.fetchone()[0]
        return self._info

    @info.setter
    def info(self, val):
        self._info = val

    @property
    def problem(self):
        if not hasattr(self, '_problem'):
            self._problem = get_problem_by_pid(self.pid)
        return self._problem

    @property
    def sid(self):
        if self._sid is None:
            self.code_for_run = self.compose()
            self._sid = self.submit()
        return self._sid

    @property
    def ctime_repr(self):
        return self.ctime[:self.ctime.index('.')]

    @property
    def state_repr(self):
        return ' '.join(word.capitalize() for word in self.state.split())

    @property
    def lang_repr(self):
        return Lang(self.lang).name

    def submit(self):
        db, c = get_db_cursor()
        c.execute('update problem set n_submissions = n_submissions + 1 ' +
                  'where rowid = ?', (self.pid,))
        ts = datetime.strftime(datetime.now(), DATETIME_FORMAT)
        c.execute('insert into submission ' +
                  '(pid, title, lang, code, ctime, state) ' +
                  'values (?,?,?,?,?,?)', (
                      self.pid, self.title, self.lang, self.code,
                      ts, 'pending'
                  ))
        c.execute('select last_insert_rowid()')
        sid = c.fetchone()[0]
        db.commit()
        return sid

    def compose(self):
        c = get_cursor()
        c.execute('select code from testcode where pid = ? and lang = ?',
                  (self.pid, self.lang))
        try:
            testcode = c.fetchone()[0]
        except TypeError:
            logging.warning('no testcode for pid == {} and lang == {}'.format(
                self.pid, self.lang
            ))
            raise Failed('No test code for problem {}'.format(self.pid))
        self.testcode = testcode
        return '\n'.join((self.code, testcode))

    def set_result(self, res):
        self.state = res.state
        self.info = res.info
        db, c = get_db_cursor()
        c.execute('update submission set state=?, info=? where rowid=?',
                  (res.state, res.info, self.sid))
        if res.state == 'accepted':
            c.execute('update problem set n_acceptions=n_acceptions + 1 ' +
                      'where rowid = ?', (self.pid,))
        db.commit()

def get_submissions():
    c = get_cursor()
    c.execute('select rowid, pid, title, lang, ctime, state from submission ' +
              'order by ctime desc limit 50')
    return [Submission.construct(*args) for args in c]

def get_submission_by_sid(sid):
    c = get_cursor()
    c.execute('select pid, title, lang, ctime, state, code ' +
              'from submission where rowid = ?', (sid,))
    pid, title, lang, ctime, state, code = c.fetchone()
    return Submission(pid=pid, title=title, lang=lang, ctime=ctime,
                      state=state, code=code, sid=sid)
