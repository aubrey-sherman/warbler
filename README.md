## Warbler

Warbler is a Flask-powered Twitter clone with functionality for users to:
* Register
* Sign in/out
* Follow/unfollow other users
* Like/unlike posts
* Update their profile
* View other user's profiles
* View a feed of posts from users they follow

Demo as a user:

Go to https://aubrey-warbler.onrender.com
Log in
* Username: tuckerdiane
* Password: password

### Installation

To run this app locally:

#### Clone the repo

```
git clone https://github.com/aubrey-sherman/warbler.git
```

#### Create the Python virtual environment

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

#### Create an .env file to hold configuration

In your .env file:

```
DATABASE_URL=postgresql:///warbler
SECRET_KEY=<your key value here>
```

#### Set up the PostgreSQL database with seeded data:
```
(venv) $ createdb warbler
(venv) $ python seed.py
```

#### Start the server
```
(venv) $ flask run -p 5001
```

#### Open in browser
http://localhost:5001

### Collaborators
[Alice Chang](https://github.com/alicechang29)