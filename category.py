from problem import Problem
from db import get_cursor

from collections import defaultdict

class Category(object):

    def __init__(self, tag, problems=None, more=False):
        self.tag = tag
        self.url_name = '-'.join(tag.split())
        self.tag_repr = ' '.join(word.capitalize() for word in tag.split())
        self.problems = problems or []
        self.more = more

def get_category_by_url_name(url_name):
    tag = ' '.join(url_name.split('-'))
    c = get_cursor()
    c.execute('select pid from tag where tag = ?', (tag,))

def get_categories():
    c = get_cursor()
    c.execute('select distinct tag from tag')
    categories = []
    for (tag,) in c.fetchall():
        category = Category(tag)
        c.execute('select count(*) from tag where tag = ?', (tag,))
        cnt = c.fetchone()[0]
        category.more = cnt > 10
        c.execute('select pid from tag where tag = ? limit 10', (tag,))
        for (pid,) in c.fetchall():
            c.execute('select title from problem where rowid = ?', (pid,))
            title, = c.fetchone()
            category.problems.append(Problem(pid, title))
        categories.append(category)
    return categories

if __name__ == '__main__':
    for tag, tag_repr, problems in get_categories():
        print '=' * 40, tag_repr
        for problem in problems:
            print problem.title
