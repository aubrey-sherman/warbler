Add route to show liked messages - DONE
Add routes for POST requests to like/unlike
Update liked_messages jinja template with correct routes for form action
Add an icon for heart (similar to Follow) onto message cards
Give functionality to that icon/button so that users can like messages
Add number of liked messages to profile page
Add link to profile page (replace TBD placeholder) to display all liked messages (similar to clicking on Following)


# Parking Lot
TODO: Update styling for uniformity
buttons in nav bar
log-in button
- add labels to the edit forms so that it's outside the box


Running questions:
- do we need form = csrf.form within followers/unfollowers? what is different about that vs log out in app.py -- only thing that looks different is that we are using it
- do we need a form.validate on submit for everything with csrf tag in app.py ?


Check in questions:
- what is the g.CsrfForm doing in the logout app.py?
- why would need to keep it as a global variable??
- TODO: STILL CONFUSED: this needs to live in global scope bc otherwise this will not carry over into other templates where logout is referenced
    - flask global obj resets before every new request.
    - it is creating a new form instance each time??
    - logout button lives in the base template
    - all other template extend base

Flask G
- it's a global object
`@app.before_request`
- Used so that we don't have to write out checking to see if the user matches the session's user
- Instead, can just reference the global object "user"
- Import it as "g" from the flask library
- calls add_user_to_g before request
    - setting the global object's "user" key value to user.id in session if it exists
    - else, global object's "user" key value is set to none
- Need to make an INSTANCE of the csrf form so that we can access it throughout our app rather than making a new instance of it every time we need a form.

global = {
    user = user.id
}

# Part 2 - Log Out and Security problems

## Logout
- Make empty CsrfForm in forms.py
- Need to fill out app.py with logout fn:


Broken:
- viewing a user when you're logged out??
- "Likes" is missing
- Edit profile
- search only allows searching for users, not posts
- messages are NOT ordered at all

Possible validation issues:
- check if form is preventing user signing up with existing username/email

Working:
- log out
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
    - signup DONE, hidden tag included already
    - login - DONE, hidden tag included already
    - adding a bio
    - edit bio - see edit notes solution doc
    - following user - DONE, added hidden tag to index.jinja and form on app.py
    - unfollowing users - DONE, same as above
    - posting messages - DONE
    - if updating messages, see notes solution doc (passing in the new message form that has all the CSRF stuff)
    - add CSRF token for log out form - DONE
    - deleting user - DONE

- Only things that don't need CSRF are:
    - Sign up Welcome page

- CHECK the AUTHORIZATION FOR GET ROUTES - DONE


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





