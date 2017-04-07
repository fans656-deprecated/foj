from db import get_cursor, get_db_cursor, connect

import threading
import multiprocessing
import Queue
import traceback
from datetime import datetime
import logging
import sys

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

class Submission(object):

    def __init__(self, pid, lang, code):
        self.pid = pid
        self.lang = lang
        self.code = code
        self.code_for_run = None
        self.state = 'pending'
        self.info = ''
        self._sid = None

    @property
    def sid(self):
        if self._sid is None:
            self.code_for_run = self.compose()
            self._sid = self.submit()
        return self._sid

    def submit(self):
        db, c = get_db_cursor()
        c.execute('update problem set n_submissions = n_submissions + 1 ' +
                  'where rowid = ?', (self.pid,))
        ts = datetime.strftime(datetime.now(), DATETIME_FORMAT)
        c.execute('insert into submission (pid, lang, code, ctime, state) ' +
                  'values (?,?,?,?,?)', (
                      self.pid, self.lang, self.code,
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

class Python2Runner(object):

    def __init__(self, q, submission):
        self.q = q
        self.submission = submission

    def start(self):
        self.thread = threading.Thread(target=self.monitor)
        self.thread.start()

    def monitor(self):
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=executor,
                                    args=(self.submission.code_for_run, q,))
        p.start()
        p.join(3.0)
        if p.is_alive():
            p.terminate()
            self.submission.set_result(Result('time limit exceeded'))
        else:
            self.submission.set_result(q.get())

class WrongAnswer(Exception):

    pass

class Result(object):

    def __init__(self, state, info=''):
        self.state = state
        self.info = info

def executor(code, q):
    env = {
        'foj': {
            'result_queue': q,
        },
        'WrongAnswer': WrongAnswer,
    }
    #logging.debug('execution')
    #logging.debug(code)
    print '=' * 40, 'execution'
    print code
    try:
        exec compile(code, '<string>', 'exec') in env
    except WrongAnswer as e:
        q.put(Result('wrong answer', e.message))
    except Exception as e:
        info = ''.join(traceback.format_exception_only(type(e), e))
        q.put(Result('runtime error', info))
    else:
        q.put(Result('accepted'))

# run failed
class Failed(Exception):

    pass

class Controller(object):

    controller = None

    def __init__(self):
        Controller.controller = self
        self.q = Queue.Queue()
        self.jobs = {}
        self.thread = threading.Thread(target=self.eventloop)

    def start(self):
        self.thread.start()

    def execute(self, submission):
        lang = submission.lang
        if lang == 'python2':
            runner = Python2Runner(self.q, submission)
            self.jobs[submission.sid] = runner
            runner.start()
        else:
            raise Failed('unsupported lang')

    def eventloop(self):
        while True:
            sid = self.q.get()
            del self.jobs[sid]

def run(pid, lang, code):
    controller = Controller.controller
    try:
        submission = Submission(pid, lang, code)
        controller.execute(submission)
        return submission.sid
    except Failed as e:
        logging.warning(e.message)
        raise
    except Exception as e:
        traceback.print_exc()
        raise Failed('unknown error')

if __name__ == '__main__':
    controller = Controller()
    code = '''
print globals().keys()
#raise WrongAnswer()
    '''
    run(1, 'python2', code)
