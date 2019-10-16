import os
import sqlite3

from flask import(Flask, request, session, g, redirect, url_for, abort, render_template, flash)

app = Flask(__name__) #create the application instance
app.config.from_object(__name__) #load the config from this file, flaskr.py

#Load default config and override config from an environment variable
app.config.update(
    DATABASE = os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY = b'M\xcd\xd9\xa5iaB\x95',
    USERNAME = 'admin',
    PASSWORD = 'default'
)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    #Connects to the specific database.

    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    #open_resource function will open a resource that the application provides
    #it opens a file from the resource location.
    #in this case it's schema.sql, then allows us to read from it.
    #The code below execute an sql script.
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    #to commit the changes you need to tell sqlite3 commit
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    #Initializes the database.

    init_db()
    print('Database Initialized!')

def get_db():
    #Opens a new database connection if there is none yet for the 
    #current application context

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    #Closes the database again at the end of the request.

    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

    #ends at page 36

#Show entries function
@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT * FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

#Add New Entry Function
@app.route('/add', methods=['POST'])
def add_entry():
    #If the user is not logged in then it will abort the function
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO entries (title,text) values(?,?)',
                [request.form['title'], request.form['text']])
    db.commit()
    flash('New Entry was successfully posted!')
    return redirect(url_for('show_entries'))

#Delete entry Function
@app.route('/delete/<int:post_id>')
def delete_entry(post_id):
    db = get_db()
    db.execute('DELETE FROM entries WHERE id = ?',[post_id])
    db.commit()
    flash('Entry deleted!')
    return redirect(url_for('show_entries'))

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid Username!'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password!'
        else:
            #create session[logged_in]
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error = error)

#Logout
@app.route('/logout')
def logout():
    #removes the key from the session if present or do nothing when key is not there
    session.pop('logged_in', None)
    flash('You were logged out!')
    return redirect(url_for('show_entries'))

#install pytest
#pip install pytest