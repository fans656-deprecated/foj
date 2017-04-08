from result import WrongAnswer

import operator

class Result(object):

    def __init__(self, args, res, eq):
        self.args = args
        self.res = res
        self.eq = eq

    def __eq__(self, expected_res):
        if callable(expected_res):
            expected_res = expected_res(*self.args)
        if not self.eq(self.res, expected_res):
            self.wrong_answer(expected_res)
        return True

    def __ne__(self, o):
        return not self.eq(self.res, o)

    def __lt__(self, o):
        return self.res < o

    def __gt__(self, o):
        return self.res > o

    def __le__(self, o):
        return self.res <= o

    def __gt__(self, o):
        return self.res >= o

    def wrong_answer(self, *expected_res):
        raise WrongAnswer(self.args, expected_res, self.res)

class Tester(object):

    def __init__(self, func, eq=operator.eq):
        self.func = func
        self.eq = eq

    def __call__(self, *args):
        try:
            res = self.func(*args)
            return Result(args, res, eq=self.eq)
        except Exception:
            raise

if __name__ == '__main__':

    def binary_search(a, x):
        b, e = 0, len(a)
        while b < e:
            m = b + (e - b) / 2
            if a[m] == x:
                return m
            elif x < a[m]:
                e = m
            else:
                b = m + 1
        return -1

    def not_in_a(*b):
        all(test(a, v) == -1 for v in b)

    def in_a():
        all(test(a, v) == i for i, v in enumerate(a))

    test = Tester(binary_search)

    test([], 0) == -1

    test([1], 0) == -1
    test([1], 1) == 0
    test([1], 2) == -1

    a = [1,2,3,4,5]
    not_in_a(0, 6)
    in_a()

    a = [1,2,3,4,5,6]
    not_in_a(0, 7)
    in_a()

    a = [1,3,5,7,9]
    not_in_a(0,2,4,6,8,10)
    in_a()

    a = [1,3,5,7]
    not_in_a(0,2,4,6,8)
    in_a()

    a = [2,2]
    not_in_a(1,3)
    r = test(a, 2)
    res = {0,1}
    if r.res not in res:
        r.wrong_answer(res)

    a = [2,2,2]
    not_in_a(1,3)
    r = test(a, 2)
    res = {0,1,2}
    if r.res not in res:
        r.wrong_answer(res)
