class WrongAnswer(Exception):

    def __init__(self, input='', expected_res='', actual_res=''):
        s = 'Input: {}\nExpect: {}\nGot: {}'.format(
            input, expected_res, actual_res
        )
        super(WrongAnswer, self).__init__(s)
