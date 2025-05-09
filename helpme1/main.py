from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
#---
from sqlalchemy.exc import IntegrityError
from typing import List
'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''
#admin account:
#admin@admin.com
#password
app = Flask(__name__, template_folder="templates")
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = SECRETKEY
Bootstrap5(app)
app.config['CKEDITOR_HEIGHT'] = 1000
app.config['CKEDITOR_WIDTH'] = 1000
ckeditor = CKEditor(app)


# TODO: Configure Flask-Login


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)




# --- USER MODEL ---
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(1000), nullable=False)

    blogs = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="comment_author", cascade="all, delete-orphan")


# --- BLOG POST MODEL ---
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    author = relationship("User", back_populates="blogs")
    blog_comments = relationship("Comment", back_populates="comment_blog", cascade="all, delete-orphan")


# --- COMMENT MODEL ---
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"), nullable=False)

    comment_author = relationship("User", back_populates="comments")
    comment_blog = relationship("BlogPost", back_populates="blog_comments")
# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.get(User, user_id)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

with app.app_context():
    db.create_all()

def admin_login_required(func):
    def wrapper(*args, **kwargs):
        if current_user.get_id() != "1":
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__ #NOTE assigning not checking (not double ==)
    return wrapper

# If you decorate a view with this, it will ensure that the current user is logged in and authenticated before calling the actual view. (If they are not, it calls the LoginManager.unauthorized callback.) For example:

#     @app.route('/post')
#     @login_required
#     def post():
#         pass

@app.route("/seed")
def seed():
    from werkzeug.security import generate_password_hash
    user = User(
        email="admin@admin.com",
        password=generate_password_hash("password", salt_length=8),
        name="Admin"
    )
    db.session.add(user)
    db.session.commit()

    post = BlogPost(
        title="Hello World",
        subtitle="First post",
        date=date.today().strftime("%B %d, %Y"),
        body="This is the first blog post.",
        img_url="https://via.placeholder.com/150",
        author=user
    )
    db.session.add(post)
    db.session.commit()
    return render_template("test.html")

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            #i am not entirely sure what the * does but code doesn't work otherwise.
            new_user = User(
                email=[*form.data.values()][0],
                password=generate_password_hash([*form.data.values()][1], salt_length=8),
                name=[*form.data.values()][2]
            )
            try:
                if new_user.email != None:
                    db.session.add(new_user)
                    db.session.commit()
                    # login_user(load_user(new_user.id))
                    return redirect(url_for('get_all_posts'))
                else:
                    pass
            except IntegrityError:
                flash("There is already a registered user under this email address.")
                return redirect("/register") #flash already registered
        else:
            pass
    else:
        pass

    return render_template("register.html", form=form)


# TODO: Retrieve a user from the database based on their email. 
# @app.route('/login', methods=["POST", "GET"])
# def login():
#     form = LoginForm()
#     password = False
#     if request.method == "POST":
#         email = request.form.get("email")
#         try:
#             requested_email = db.session.execute(db.select(User).filter(User.email == email)).scalar_one()
#             print(request.form.get("password"))
#             password = check_password_hash(requested_email.password, request.form.get("password"))
#             if password == True:
#                 print("success")
#                 print(load_user(requested_email.id))
#                 try:
#                     print(load_user(requested_email.id))
#                     login_user(load_user(requested_email.id))
#                 except:
#                     print("ass")
#             else:
#                 print("incorrect pass")
#         except Exception as e:
#             print("incorrect pass2")
    
#     return render_template("login.html", form=form)
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/', methods=["GET", "POST"])
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, user=current_user.get_id())


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            text=form.comment.data,
            # author=current_user,
            # date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("post.html", post=requested_post, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
