from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_security import RoleMixin
from flask_security import UserMixin
from flask_security import current_user
from flask_security import login_required
from flask_security.forms import RegisterForm
from flask_security.forms import LoginForm

from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm 
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Institute for Intelligence and Secret Operations'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'Salt secret string against dictionary attacks'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'username'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

'''
First we must configurate the Flask application. Our database will be called "database.db". After this we set the false
value of the SQLALHEMY_TRACK_MODIFICATIONS in order to pass the warning that SQLAlchemy will add additional overhead. By
setting the value of this configuration to False, we won't see this message. The DEBUG value will be True in order to pass
specific errors that may occur with our application. The Secret Key will be used for securely signing the session cookie.
The SECURITY_REGISTERABLE specifies that Flask Security should create a user registration endpoint. The SECURITY_PASSWORD_SALT
will be used against any dictionary attacks. What is the logic behind the SALT defence? First we have a password and one
random generated string (the one from above). Before hashing the password, first our application will concatenate our
password with this string and will hash the concatenated result, not just the password. This will help us to prevent from
such kind of attacks. The SECURITY_SEND_REGISTER_EMAIL will accept valid emails, but later on the login form we will use the
Username instead of this Email.

(Important: Flask Security uses another folder for the templates of the register and the login page, which folder must be called
"security". Above we haven't added these two lines of code:

app.config[SECURITY_REGISTER_USER_TEMPLATE] = random_register_name_template.html
app.config[SECURITY_LOGIN_USER_TEMPLATE] = random_login_user_template.html

We haven't added them because, by default the templates for these 2 pages are in the folder "security" and are "security/register_user.html"
and "security/login_user.html". As we haven't specified another names for them, we should call our templates in this folder this way.)

To make all of this I read from the following documentation: https://flask-security-too.readthedocs.io/_/downloads/en/stable/pdf/
'''

db = SQLAlchemy(app)
migrate = Migrate(app, db)

'''
We use SQLAlchemy ORM (Object-relational mapping) for our database and Migrate to migrate the data correctly. It is important to say here,
that this extension configures Alembic in the proper way to work with our application database and this will help us. Then, the first table,
which we will create is the one making the relation between the RoleMixin and UserMixin. The Role Mixin class has members for the
name and the description. The first one should be UNIQUE, and both of them can't be NULL. The User Mixin class has members for the
ID number, the email address, the password, the name, the username, a boolean variable, which will show if the user is active or not (this
we will need later in the application) and the default variable from type DATETIME confirmed_at. Then we has a FOREIGN KEY to the roles_users
table and a FOREIGN KEY to the posts (this we will need later too). Every class will be a database model of SQLAlchemy. In the reference we
say that "lazy='dynamic'". This means that we will return an object if our list from posts, for example, is very big, so this will be an
object, but not simply a list as expected.
'''

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(2000), unique=False, nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='user', lazy='dynamic')


class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(2000), unique=False, nullable=False)
    date_created = db.Column(db.DateTime())
    posts = db.relationship('Post', backref='topic', lazy='dynamic')


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2000))
    date_created = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

class New_Topic(FlaskForm):
    title = StringField('Title')
    description = StringField('Description')

class New_Post(FlaskForm):
    content = TextAreaField('Content')

'''
For topics and posts we will have different classes. This means that we will have two different tables for them. The table for
the topics has a title, a description, a variable, which will help us to determine when exactly was the topic created (used later
just in the information of the HTML page of every different topic) and a relation to the topics. The relation here is 1:N, because
one topic will contain many posts. The table for the posts will has content, again a variable from type DATETIME and a reference to 2
things: in which topic exactly is a given post and by who is published on this topic. We has two more classes, that, in fact, will be
the register forms for adding new topic and adding new post. The first one is different from the second one by one thing - the first
will expect a shorter strings in its fields. (StringField by default accepts just one line, but TextAreaField is supposed to be used
for bigger strings, that will have the form of a real text.)
'''

class ExtendRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')

class ExtendLoginForm(LoginForm):
    email = StringField('Username', [InputRequired()])


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendRegisterForm, login_form=ExtendLoginForm)

'''
The ExtendRegisterForm and ExtendLoginForm classes extend the fields for the register page and the login page. By default, Flask Security
supports only 3 fields for the register page - one for entering an email address, one for entering a password and one for repeating this
password. In the exercise is said that we will have to use the username to login into our account, and thats why on every registration page
we add 2 more field for entering - a new name and a new username (the new name is not compulsory, but is a good practise to have one on the
register page). Flask Security uses 2 fields for the login page - one for entering the email address of the user and one for entering the
password of the same user. At the end, we have to specify the different register and login forms in Flask Security with the new ones.
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    form = New_Topic()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_topic = Topic(title=form.title.data, description=form.description.data, date_created=datetime.now())
            db.session.add(new_topic)
            db.session.commit()
        except:
            return "There was a problem adding a new topic!"

    topics = Topic.query.all()
    return render_template('index.html', form=form, topics=topics, current_user=current_user)

@app.route('/topic/<topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    form = New_Post()
    topic = Topic.query.get(int(topic_id))

    if request.method == 'POST' and form.validate_on_submit():
        try:
            post = Post(user_id=current_user.id, content=form.content.data, date_created=datetime.now())
            topic.posts.append(post)
            db.session.commit()
        except:
            return "There was a problem adding a new post on this topic!"

    posts = Post.query.filter_by(topic_id=topic_id).all()
    return render_template('topic.html', topic=topic, form=form, posts=posts, current_user=current_user)

@app.route('/delete/<int:id>')
def delete_post(id):
    post_to_delete = Post.query.get(int(id))
    
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(request.referrer)
    except:
        return "There was a problem deleting this post!"

'''
What is the logic behind all the functions for the routes here?

1. index() - used to adding new topics by a user
The index function will be the function for the root page. On the root page, as it is said in the exercise, everyone
shoud see the list with the topics. In the beginning of the function we call db.create_all() to create the database in
case the application creates it for first time. When we want to create a new topic, we will have a POST method. First
we will use our Flask Form to enter the data for the new topic (its title and description). If the validation from the
form is OK, then we make a new instance of the topic class with these data from the form and the datetime of creating
the topic. Then we add this new topic to the database and make a commit. At the end, we must query all the topics from
the database. We do this in order to show on the webpage all of the topics, even with the new ones added.

2. topic() - used for adding new posts to a given topic by a user
The topic function is analogial to the index function. First we will have Flask Form to get the inputed content of the
post. First of all, we should know exactly on which topic we are and where we add our new post. We will find our wanted
topic by the ID number from the database. Again, if the validation for the form is OK, we make a new instance of the
class Post and add this new instance to our list of posts on the given topic. After this we commit and we are ready to
get our new list of posts, searching them in the database and filtering them by the ID number of our current topic.

3. delete_post() - used for deleting a post from a given topic by a user
To delete a post, we simply search through the database the ID number of the post, which we want to delete, then we
delete this post from the database and commit the result. At the end we redirect to the same page of the current topic.

'''

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post_to_update = Post.query.get(int(id))
    if request.method == 'POST':
        post_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect(request.referrer)
        except:
            return "There was a problem updating that post!"
    else:
        return render_template('update.html', post_to_update=post_to_update)

'''
The operation for updating a post is started and is not fully ready yet,
because it is supposed to be finished by my colleague in the team. The splitting
the models in different files (because it is a good practise) is up to him again. 
'''
