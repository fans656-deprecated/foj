from db import get_cursor, get_db_cursor, connect
from problem import get_problem_by_pid
from tester import Tester
from result import WrongAnswer
from lang import Lang
from submission import Submission

import threading
import multiprocessing
import Queue
import traceback
import logging
import sys

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

class Result(object):

    def __init__(self, state, info=''):
        self.state = state
        self.info = info

def executor(code, q):
    env = {
        'Tester': Tester,
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

def run(pid, title, lang, code):
    controller = Controller.controller
    try:
        submission = Submission(pid, title, lang, code)
        controller.execute(submission)
        return submission.sid
    except Failed as e:
        logging.warning(e.message)
        raise
    except Exception as e:
        traceback.print_exc()
        raise Failed('unknown error')

if __name__ == '__main__':
    print get_submissions()
