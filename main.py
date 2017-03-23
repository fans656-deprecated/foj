from problems import (
    get_problems, get_problem, get_new_problem_id,
    get_cur_problem_id, get_db, get_cursor, get_db_cursor, Problem,
)

from flask import Flask, render_template, url_for, request

import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', get_problems=get_problems)

@app.route('/problems/<url_name>')
def problem(url_name):
    return render_template('problem.html', problem=get_problem(url_name))

@app.route('/add-problem')
def add_problem():
    return render_template('add_problem.html', problem_id=get_new_problem_id())

@app.route('/submit-problem', methods=['POST'])
def submit_problem():
    form = request.form
    p = Problem(form['title'],
                desc=form['desc'],
                testcases=form['testcases'],
                pid=get_new_problem_id())
    db, c = get_db_cursor()
    c.execute('insert into problems values (?, ?, ?, ?, ?)', p.as_tuple())
    db.commit()
    return 'ok'

@app.route('/submit-code', methods=['POST'])
def submit_code():
    form = request.form
    lang = form['lang']
    p = Problem.from_id(form['pid'])
    try:
        sid = p.submit(lang=lang, code=form['code'])
        return str(sid)
    except RuntimeError as e:
        return e.message
    print 'oops'

@app.route('/code-for')
def code_for():
    args = request.args
    title = args.get('title')
    lang = args.get('lang')
    c = get_cursor()
    c.execute('select id from problems where title = ?', (title,))
    pid = c.fetchone()[0]
    c.execute('select {}_code from problem where id = ?'.format(lang),
              (pid,))
    code = c.fetchone()[0]
    return code.strip()

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **vals):
    if endpoint == 'static':
        filename = vals.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            vals['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **vals)

if __name__ == '__main__':
    app.run(host='localhost', port=80, debug=True)
