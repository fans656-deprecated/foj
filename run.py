from db import get_db, get_cursor, get_db_cursor

from multiprocessing import Process, Queue
import threading
import time

def execute_code(code):
    exec compile(code, '<string>', 'exec')

def monitor(p, duration=1.0):
    p.start()
    beg = time.time()
    while p.is_alive():
        elapsed = time.time() - beg
        if elapsed > duration:
            print 'TLE, terminate'
            p.terminate()
            break

def run_submission(sid, problem, lang, code):
    testcode = problem.testcode
    runcode = '\n'.join((code, testcode))
    print runcode
    p = Process(target=execute_code, args=(runcode,))
    threading.Thread(target=monitor, args=(p,)).start()

if __name__ == '__main__':
    from problems import Problem
    p = Problem(0, 'foo', testcode='')
    run_submission(0, p, 'python', 'print "hello"')
    time.sleep(1)
