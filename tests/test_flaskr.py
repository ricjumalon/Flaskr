import os
import tempfile
import pytest
from flaskr import flaskr

"""
This client fixture will be called by each individual test.
It gives us a simple interface to the application, where we can trigger
test requests to the application. The client will also keep track of cookies
"""
@pytest.fixture
def client():
    #Creates a temporary database and initialize it.
    db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    flaskr.app.config['TESTING'] = True
    client = flaskr.app.test_client()

    with flaskr.app.app_context():
        flaskr.init_db()

    yield client

    os.close(db_fd)
    os.unlink(flaskr.app.config['DATABASE'])

#Test the database if its empty
def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'No entries here so far' in rv.data

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects = True)

def logout(client):
    return client.get('/logout', follow_redirects = True)

#Testing login_logout
def test_login_logout(client):
    """Make sure login and logout works."""

    rv = login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
    assert b'You were logged in' in rv.data

    rv = logout(client)
    assert b'You were logged out' in rv.data

    rv = login(client, flaskr.app.config['USERNAME'] + 'x', flaskr.app.config['PASSWORD'])
    assert b'Invalid Username!' in rv.data #Your error text in the login should be the same on this assert error message

    rv = login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'] + 'x')
    assert b'Invalid Password!' in rv.data #Your error text in the login should be the same on this assert error message

#Test Add Entry Function
def test_messages(client):
    """Test that messages work."""

    login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
    rv = client.post('/add', data=dict(
        title = '<Hello>',
        text = '<strong>HTML</strong> allowed here'
    ), follow_redirects=True)
    assert b'No entries here so far' not in rv.data
    assert b'&lt;Hello&gt;' in rv.data
    assert b'<strong>HTML</strong> allowed here' in rv.data

#Test Delete Entry Function
def test_delete(client):

    login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
    rv = client.post('/add', data=dict(
        title = '<Hello>',
        text = '<strong>HTML</strong> allowed here'
    ), follow_redirects=True)

    rv = client.get('/delete/?id=1')
    assert b'No entries here so far' not in rv.data
