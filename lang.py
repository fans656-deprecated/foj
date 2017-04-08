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
