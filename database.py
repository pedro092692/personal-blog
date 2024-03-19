from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from slugify import slugify
from datetime import date
from flask_login import UserMixin
from typing import List
import os


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# Create extension
db = SQLAlchemy(model_class=Base)


# CONFIGURE TABLES

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(1000), nullable=False)
    posts: Mapped[List["BlogPost"]] = relationship(back_populates="author")
    comments: Mapped[List["Comment"]] = relationship(back_populates="comment_author")

    def __repr__(self):
        return f"<User {self.email}>"

    @staticmethod
    def users():
        users = db.session.execute(db.select(Users).order_by(Users.email)).scalars().all()
        return users

    @staticmethod
    def crete(name, email, password):
        new_user = Users(
            name=name,
            email=email,
            password=password
        )
        return new_user

    @staticmethod
    def check_user(email):
        user = Users.query.filter_by(email=email).first()
        if user:
            return user


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    author: Mapped["Users"] = relationship(back_populates='posts')
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    comments: Mapped[List["Comment"]] = relationship(back_populates="parent_post")

    def __repr__(self):
        return f"<BlogPost {self.slug}>"

    @staticmethod
    def posts():
        posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.title)).scalars().all()
        return posts


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    comment_author: Mapped["Users"] = relationship(back_populates='comments')
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_posts.id"))
    parent_post: Mapped[List["BlogPost"]] = relationship(back_populates='comments')


class Database:

    def __init__(self, app):
        self.db = db
        self.app = app

        # Database init
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///blog.db')
        self.db.init_app(self.app)

    @staticmethod
    def get_date():
        today = date.today()
        formatted_date = today.strftime("%B %d, %Y")
        return formatted_date

    def create_tables(self):
        with self.app.app_context():
            self.db.create_all()

    def get(self, table, record_id):
        return self.db.get_or_404(table, record_id)

    # Users
    @staticmethod
    def users():
        return Users.users()

    def create_user(self, name, email, password):
        new_user = Users.crete(name, email, password)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    @staticmethod
    def user_exist(email):
        return Users.check_user(email)

    # Posts
    @staticmethod
    def posts():
        return BlogPost.posts()

    def create_post(self, user_id, title, subtitle, body, img_url):

        slug = slugify(title)
        unique_slug = slug
        count = 1

        while BlogPost.query.filter_by(slug=unique_slug).first():
            unique_slug = f'{slug}-{count}'
            count += 1

        new_post = BlogPost(
            user_id=user_id,
            title=title,
            subtitle=subtitle,
            date=self.get_date(),
            body=body,
            img_url=img_url,
            slug=unique_slug,
        )

        self.db.session.add(new_post)
        self.db.session.commit()

        return new_post

    def get_post(self, slug):
        post = self.db.first_or_404(self.db.select(BlogPost).filter_by(slug=slug))
        return post

    def edit_post(self, slug, title, subtitle, body, img_url):
        post = self.get_post(slug)
        post.title = title
        post.subtitle = subtitle
        post.body = body
        post.img_url = img_url
        self.db.session.commit()

    def delete_post(self, slug):
        post = self.get_post(slug)
        self.db.session.delete(post)
        self.db.session.commit()

    # Comments
    def create_comment(self, user_id, comment, post_id):
        new_comment = Comment(
            user_id=user_id,
            comment=comment,
            post_id=post_id
        )

        self.db.session.add(new_comment)
        self.db.session.commit()

