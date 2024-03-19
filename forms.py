from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField


def name_field():
    return StringField(label='Name', validators=[DataRequired()])


def email_field():
    return EmailField(label='Email', validators=[DataRequired(), Email()])


def password_field():
    return PasswordField(label='Password', validators=[DataRequired()])


def submit_field(label):
    return SubmitField(label=label)


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = submit_field(label='Submit Post')


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = name_field()
    email = email_field()
    password = password_field()
    submit = submit_field(label='Sing me up!')


# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = email_field()
    password = password_field()
    submit = submit_field(label='Let me in!')


# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = CKEditorField(label='Comment', validators=[DataRequired()])
    submit = submit_field(label='Submit comment')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = email_field()
    phone = StringField('Phone Number')
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=30)])
    submit = submit_field(label='Send Message')



