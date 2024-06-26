import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized


from forms import UserAddForm, LoginForm, MessageForm, CsrfForm, EditUserProfileForm
from models import db, dbx, User, Message, Like, DEFAULT_IMAGE_URL, DEFAULT_HEADER_IMAGE_URL

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

db.init_app(app)


##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global.
    """
    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_form_to_g():
    """Add instance of CSRF form to the Flask global object."""

    g.csrf_form = CsrfForm()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.jinja', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.jinja', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data,
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.jinja', form=form)


@app.post('/logout')
def logout():
    """Handle logout of user and redirect to homepage."""
    form = g.csrf_form

    if form.validate_on_submit():
        do_logout()

        flash(f"Log out successful.", "success")

        return redirect("/login")

    else:
        # didn't pass CSRF; ignore logout attempt
        raise Unauthorized()

    # DO NOT CHANGE METHOD ON ROUTE


##############################################################################
# General user routes:

@app.get('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = request.args.get('q')

    if not search:
        q = db.select(User).order_by(User.id.desc())

    else:
        q = db.select(User).filter(User.username.like(f"%{search}%"))

    users = dbx(q).scalars().all()

    return render_template('users/index.jinja', users=users)


@app.get('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = db.get_or_404(User, user_id)

    return render_template('users/show.jinja', user=user)


@app.get('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = db.get_or_404(User, user_id)
    return render_template('users/following.jinja', user=user)


@app.get('/users/<int:user_id>/followers')
def show_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = db.get_or_404(User, user_id)
    return render_template('users/followers.jinja', user=user)


@app.post('/users/follow/<int:follow_id>')
def start_following(follow_id):
    """Add a follow for the currently-logged-in user.

    Redirect to following page for the current user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    if form.validate_on_submit():
        followed_user = db.get_or_404(User, follow_id)
        g.user.follow(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


@app.post('/users/stop-following/<int:follow_id>')
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user.

    Redirect to following page for the current for the current user.
    """

    form = g.csrf_form

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if form.validate_on_submit():

        followed_user = db.get_or_404(User, follow_id)

        g.user.unfollow(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")

# TODO: Add routes here for showing liked messages, like, unlike


@app.get('/users/<int:user_id>/liked-messages')
def show_liked_messages(user_id):

    # do security check; raise Unauthorized if it fails
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = db.get_or_404(User, user_id)
    # get data of liked messages from property method on user
    liked_messages = g.user.likes
    # [<Like 89, 1>, <Like 89, 2>]

    liked_message_ids = [msg.message_id for msg in liked_messages]
    # [1,2]

    # given a list of message id's, get all the message instances out
    # and put it in a list

    q = (
        db.select(Message)
        .where(Message.id.in_(liked_message_ids))
        .order_by(Message.timestamp.desc())
    )

    liked_messages = dbx(q).scalars().all()
    # [<Message 2>, <Message 1>]

    # feed that data into the jinja template
    return render_template(
        '/users/liked_messages.jinja', user=user, liked_messages=liked_messages)


@app.post('/messages/<int:message_id>/like')
def like_message(message_id):
    """Have currently-logged-in-user like a message.
    Redirect to liked messages page for the current user."""
    # first, authorization check
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    if form.validate_on_submit():
        # add message instance to list of liked messages
        msg = db.get_or_404(Message, message_id)
        like = Like(message_id=msg.id, user_id=g.user.id)
        # commit to database
        db.session.add(like)
        db.session.commit()

        url_came_from = request.form["url_came_from"]

        # user can like/unlike on many different pages
        return redirect(url_came_from)

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


@app.post('/messages/<int:message_id>/unlike')
def unlike_message(message_id):
    """Have currently-logged-in-user unlike a message.
    Redirect to liked messages page for the current user."""
    # first, authorization check
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form
    if form.validate_on_submit():

        q = db.select(Like).filter_by(user_id=g.user.id, message_id=message_id)

        like = dbx(q).scalars().one()

        db.session.delete(like)
        db.session.commit()

        url_came_from = request.form["url_came_from"]

        # user can like/unlike on many different pages
        return redirect(url_came_from)

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


@app.route('/users/profile', methods=["GET", "POST"])
def update_profile():
    """Update profile for current user if user is authorized to do so.
        Unauthorized users will be redirected to the homepage.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = EditUserProfileForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(
                username=g.user.username,
                password=form.password.data):
            try:
                g.user.username = form.username.data
                g.user.email = form.email.data
                g.user.bio = form.bio.data
                g.user.image_url = form.image_url.data or DEFAULT_IMAGE_URL
                g.user.header_image_url = (
                    form.header_image_url.data or DEFAULT_HEADER_IMAGE_URL)

                db.session.commit()
                return redirect(f"/users/{g.user.id}")

            except IntegrityError:
                flash("Username or Email taken")
                db.session.rollback()
                return render_template("/users/edit.jinja", form=form)

        else:
            flash("Password Incorrect", "danger")
            return render_template("/users/edit.jinja", form=form)
    else:
        return render_template("/users/edit.jinja", form=form)


@app.post('/users/delete')
def delete_user():
    """Delete user.

    Redirect to signup page.
    """
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    if form.validate_on_submit():
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

        flash("Account successfully deleted.")

        return redirect("/signup")
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def add_message():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/create.jinja', form=form)


@app.get('/messages/<int:message_id>')
def show_message(message_id):
    """Show a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = db.get_or_404(Message, message_id)
    return render_template('messages/show.jinja', message=msg)


@app.post('/messages/<int:message_id>/delete')
def delete_message(message_id):
    """Delete a message.

    Check that this message was written by the current user.
    Redirect to user page on success.
    """

    form = g.csrf_form

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if form.validate_on_submit():
        msg = db.get_or_404(Message, message_id)
        db.session.delete(msg)
        db.session.commit()
        return redirect(f"/users/{g.user.id}")

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


##############################################################################
# Homepage and error pages


@app.get('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of self & followed_users
    """
    if g.user:

        # get id for each followed instance in list of who the user is following
        followed_ids = [followed.id for followed in g.user.following]

        followed_ids.append(g.user.id)

        q = (
            db.select(Message)
            .where(Message.user_id.in_(followed_ids))
            .order_by(Message.timestamp.desc())
            .limit(100)
        )

        messages = dbx(q).scalars().all()

        return render_template('home.jinja', messages=messages)

    else:
        return render_template('home-anon.jinja')


@ app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True

    return response
