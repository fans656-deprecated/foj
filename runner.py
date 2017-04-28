from db import get_cursor, get_db_cursor, connect
from problem import get_problem_by_pid
from tester import Tester
from result import WrongAnswer
from lang import Lang
from submission import Submission

import os
import sys
import threading
import multiprocessing
import Queue
import traceback
import logging
import tempfile
import shutil

class Python2Runner(object):

    def __init__(self, q, submission):
        self.q = q
        self.submission = submission

    def start(self):
        self.thread = threading.Thread(target=self.monitor)
        self.thread.start()

    def monitor(self):
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=python_executor,
                                    args=(self.submission.code_for_run, q,))
        p.start()
        p.join(3.0)
        if p.is_alive():
            p.terminate()
            self.submission.set_result(Result('time limit exceeded'))
        else:
            self.submission.set_result(q.get())
        self.q.put(self.submission.sid)

def python_executor(code, q):
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

class CppRunner(object):

    class Env(object):

        def __init__(self, submission):
            self.submission = submission

        def __enter__(self):
            submission = self.submission
            sid = submission.sid
            dirpath = tempfile.mkdtemp(prefix='foj-cpp-{}-'.format(sid))
            test_fpath = os.path.join(dirpath, 'test.h')
            main_fpath = os.path.join(dirpath, 'main.cpp')
            with open(test_fpath, 'w') as f:
                f.write(submission.testcode)
            with open(main_fpath, 'w') as f:
                f.write(CPP_RUNCODE_TEMPLATE.format(code=submission.code))
            self.dirpath = dirpath
            self.test_fpath = test_fpath
            self.main_fpath = main_fpath
            return self

        def __exit__(self, *_):
            #shutil.rmtree(self.dirpath)
            pass

    def __init__(self, q, submission):
        self.q = q
        self.submission = submission

    def start(self):
        self.thread = threading.Thread(target=self.monitor)
        self.thread.start()

    def monitor(self):
        with CppRunner.Env(self.submission) as env:
            p = multiprocessing.Process(
                target=cpp_executor, args=(env.dirpath,))
            p.start()
            p.join()
        self.q.put(self.submission.sid)

def cpp_executor(cwd):
    os.chdir(cwd)
    os.system('g++ --std=c++11 -o main.exe main.cpp')
    os.system('main.exe')

class Result(object):

    def __init__(self, state, info=''):
        self.state = state
        self.info = info

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
        ConcreteRunner = None
        if lang == 'python2':
            ConcreteRunner = Python2Runner
        elif lang == 'cpp':
            ConcreteRunner = CppRunner
        if ConcreteRunner:
            runner = ConcreteRunner(self.q, submission)
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

CPP_RUNCODE_TEMPLATE = '''\
#include <cstdio>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include "../../foj.h"
#include "test.h"

using namespace std;

{code}

int main() {{
    test();
}}'''

if __name__ == '__main__':
    print get_submissions()
