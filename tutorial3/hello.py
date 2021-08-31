# imports
from __future__ import with_statement
from contextlib import closing
import os
import sqlite3
from flask import Flask, request, session, g, redirect
from flask import url_for, abort, render_template, flash



# configuration
DATABASE = 'db/hello.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


# db function
def connect_db():
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        return conn
    except sqlite3.OperationalError:
        return None

def create_connection(db_file):
    print('create a database connection to a SQLite database ==> ' + db_file)
    conn = None
    folderpath = os.path.split(os.path.abspath(db_file))[0]
    if os.path.isdir(folderpath) == False:
        os.mkdir(folderpath)

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()

def init_db():
    db = connect_db()
    if db is None:
        create_connection(app.config['DATABASE'])
        db = connect_db()

        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()
    print('db connection done')


app = Flask(__name__)
app.config.from_object(__name__)
print('flask starting...')
init_db()

#  app routing 
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/hello')
def hello_sub():
    return 'Hello World sub hello!'

@app.route('/homepage')
def hello_homepage(name=None):
    return render_template('hello.html', name=name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()