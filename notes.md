Check in questions:
- what is the g.CsrfForm doing in the logout app.py?
- why would need to keep it as a global variable??

Flask G
- it's a global object
`@app.before_request`
- Used so that we don't have to write out checking to see if the user matches the session's user
- Instead, can just reference the global object "user"
- Import it as "g" from the flask library
- calls add_user_to_g before request
    - setting the global object's "user" key value to user.id in session if it exists
    - else, global object's "user" key value is set to none

global = {
    user = user.id
}

# Part 2 - Log Out and Security problems

## Logout
- Make empty CsrfForm in forms.py
- Need to fill out app.py with logout fn:
```python
@app.post("/logout")
def logout():
    """Logout. Redirects to login page."""

    form = CsrfForm()

    if form.validate_on_submit():
        session.pop(AUTH_KEY) #FIXME: CHANGE THIS TO LOGOUT fn from global fns
        return redirect("/login")

    else:
        # didn't pass CSRF; ignore logout attempt
        raise Unauthorized()
```
- Currently, log out button is an a tag. need to change it to a form
```jinja
      <form>
        <button class="btn btn-danger btn-sm"
                formaction="/logout"
                formmethod="POST">
          Logout
        </button>
      </form>
```


Broken:
- log out
- viewing a user when you're logged out??
- "Likes" is missing
- Edit profile
- search only allows searching for users, not posts
- messages are NOT ordered at all
-

Possible validation issues:
- check if form is preventing user signing up with existing username/email

Working:
- register
- add prof pic on register
- login
- following / unfollowing
- posting messages
- deleting message
- delete profile

# Security:
- authorization
- Any changes that involve the DB needs a CSRF token
- CSRF tokens - check if ea form is a flask form
    - registration
    - login
    - adding a bio
    - edit bio - see edit notes solution doc
    - following user
    - unfollowing users
    - posting messages
    - if updating messages, see notes solution doc (passing in the new message form that has all the CSRF stuff)
    - add CSRF token for log out form
    - deleting user


- Only things that don't need CSRF are:
    - Sign up Welcome page


- is this action changing the world

- TODO: check if we are saving the username in the session
    -   does the session value found in browser represent the username/id?

in app.py

```python
##AUTH_KEY is always the string "username"
CURR_USER_KEY = "curr_user"

#The value of AUTH_KEY will be accessed via session[AUTH_KEY] to get the username of the instance. This is done on registration / login
session[CURR_USER_KEY] = user.id

#if AUTH_KEY not in session >> checking if user is authenticated
if CURR_USER_KEY not in session or username != session[CURR_USER_KEY]:
        raise Unauthorized()
```
1. Pay attention to where session[curr_user_key] is being:
    - set: upon registration / login
    - cleared: upon log out


# Models

## Follow
- connecting follower and followed user
- unique constraints on user being followed and user following id
    - both id's are primary keys bc can't have 1 user following same person multiple times

1 User: Have Many Followers
1 User: Follow Many Users

Follow represents the relationship between users (1 user to another)
(middle join table - followers table)
eg: matches are another expression of a relationship between 2 users


(1 song > many playlists)
(1 playlist > many songs)
instead of song/playlist on the 1 side, we have 1 user

Follow and Messages don't have relationship with each other
User > Followers (Many)
User > Following (Many)
User > Messages (Many)

## User
- user id is primary key
- unique username/email
- message back-populates (message has its own table)
- signup method
- authenticate method
- functions for checking for followers

## Message
- id = primary key
- user_id is the foreign key
- back-populates messages





