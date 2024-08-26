# Warbler

Warbler is a Flask-powered Twitter clone with functionality for users to:
    - register
    - sign in/out
    - follow/unfollow other users
    - like/unlike 'warbles' (posts) by other users
    - write 'warbles'
    - update their profiles

## Installation

# Create the Python virtual environment

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

# Create an .env file to hold configuration with your SECRET_KEY and DATABASE_URL

# Set up the database:
```
(venv) $ createdb warbler
(venv) $ python seed.py
```

# Start the server
```
(venv) $ flask run
```
OR

```
flask run -p 5001
```

^^ This second command is necessary on Macs that already have port 5000 in use.

# Open http://localhost:5000 or http://localhost:5001 in your browser

# Collaborators
[Alice Chang](https://github.com/alicechang29)