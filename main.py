from flask import Flask, render_template, redirect, url_for, flash, request
from database import Database, BlogPost, Users
from flask_bootstrap import Bootstrap5
from ckEditor import Editor
from flask_gravatar import Gravatar
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm
from helpers import Helper, is_admin
from send_email import Email
from dotenv import load_dotenv
import os


# Load env
load_dotenv()

# Init app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Database
db = Database(app)
# Creates tables
db.create_tables()

# Plugins
editor = Editor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
Bootstrap5(app)
helper = Helper()
email = Email()
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None
                    )

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)


# TODO: Configure Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.get(Users, user_id)


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        if db.user_exist(email):
            flash(f"You've already signed up with {email}, log in instead!")
            return redirect(url_for('login', email=email))
        else:
            new_user = db.create_user(
                name=form.name.data,
                email=email,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
            )

            login_user(new_user)

            return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=form)


# TODO: Retrieve a user from the database based on their email.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('get_all_posts'))

    email_login = helper.check_url_var('email')
    form = LoginForm(
        email=email_login
    )
    if form.validate_on_submit():
        email_login = form.email.data
        password = form.password.data
        user = db.user_exist(email_login)
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Invalid User or Password')

        else:
            flash('Invalid User or Password')
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    posts = db.posts()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<slug>", methods=['GET', 'POST'])
def show_post(slug):
    requested_post = db.get_post(slug)
    form = CommentForm()
    if form.validate_on_submit():
        comment = form.comment.data
        if current_user.is_authenticated:
            db.create_comment(
                user_id=current_user.id,
                comment=comment,
                post_id=requested_post.id
            )
        else:
            flash('You need to logging to comment.')
            return redirect(url_for('login'))
    return render_template("post.html", post=requested_post, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@login_required
@is_admin
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = db.create_post(
            user_id=current_user.id,
            title=form.title.data,
            subtitle=form.subtitle.data,
            img_url=form.img_url.data,
            body=form.body.data
        )

        return redirect(url_for('show_post', slug=new_post.slug))

    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<slug>", methods=["GET", "POST"])
@login_required
@is_admin
def edit_post(slug):
    post = db.get_post(slug)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body,
    )

    if edit_form.validate_on_submit():
        db.edit_post(
            slug=slug,
            title=edit_form.title.data,
            subtitle=edit_form.subtitle.data,
            img_url=edit_form.img_url.data,
            body=edit_form.body.data
        )

        return redirect(url_for('show_post', slug=slug))

    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<slug>")
@login_required
@is_admin
def delete_post(slug):
    db.delete_post(slug)
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    mgs_send = False
    if form.validate_on_submit():
        email_address = form.email.data
        message = f"{form.name.data} wants to contact to you:\n" \
                  f"{form.message.data}\n" \
                  f"Email address: {form.email.data}\n" \
                  f"Phone Number {form.phone.data}"

        if email.send_email(message=message.encode('latin1', 'ignore')):
            mgs_send = True

    return render_template("contact.html", form=form, mgs_send=mgs_send)


# Errors
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('get_all_posts'))


@app.errorhandler(401)
def custom_401(error):
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=False)
