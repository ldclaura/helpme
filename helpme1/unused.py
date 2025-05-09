
# TODO: Create a User table for all your registered users. 
class User(UserMixin, db.Model): #NOTE i didnt have UserMixin, you need that for login to work.
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    # blogs: Mapped[List["BlogPost"]] = relationship(back_populates="author") #does not create table section
    # comments: Mapped[List["Comment"]] = relationship(back_populates="comment_author")#does not create section in table
    blogs = relationship("BlogPost", back_populates="author") #does not create table section
    comments = relationship("Comment", back_populates="comment_author")#does not create section in table

# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # author: Mapped["User"] = relationship(back_populates="blogs") #does not create section in table
    # blog_comments: Mapped["Comment"] = relationship(back_populates="comment_blog")#does not create section in table
    author = relationship("User", back_populates="blogs") #does not create section in table
    blog_comments = relationship("Comment", back_populates="comment_blog")#does not create section in table
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # comment_author: Mapped["User"] = relationship(back_populates="comments")#does not create section in table
    # comment_blog: Mapped["BlogPost"] = relationship(back_populates="blog_comments")#does not create section in table
    comment_author = relationship("User", back_populates="comments")#does not create section in table
