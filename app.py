from flask import Flask, flash, redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import *
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import time
from datetime import *
from wtforms.widgets import TextArea

###--------------------------
# App Configuration
###--------------------------

app = Flask(__name__)
Bootstrap(app)
app.secret_key = "pickaprivatekeyplease"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
firstTime = False

class PostForm(FlaskForm):
    username = StringField('Enter your username.')
    content = StringField('Leave us a post here.', widget=TextArea())

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    content = db.Column(db.String(144))
    date = db.Column(db.String(10))
    show = db.Column(db.Integer)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

###--------------------------
# Template Rendering
###--------------------------
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def index():
    all_posts = Posts.query.all()
    all_posts.reverse()

    return render_template('index.html', all_posts=all_posts)

@app.route("/post", methods=['GET', 'POST'])
def post():
    form = PostForm()
    today = str(date.today())
    if form.validate_on_submit():
        try:
            new_post = Posts(username=str(form.username.data), content=str(form.content.data), date=today, show=1)
            db.session.add(new_post)
            db.session.commit()
            print("New post added successfully!")
            return render_template('index.html')
        except:
            print("Hmmm...")
            flash("Uh oh, something went wrong.")

    return render_template('post.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    global current_user
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        current_user = Users.query.filter_by(username=username).first()

        if current_user:
            if current_user.password == password:
                login_user(current_user)
                print("Auth?: " + str(current_user.is_authenticated))
                username=current_user.username
                return redirect(url_for('index'))
            else:
                error='Invalid Credentials. Please try again.'
                flash("Wrong Password")
                print(current_user.password)
        else:
            error='You have not signed up for an account yet.'


    return render_template('login.html', error=error)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/delete/<content>", methods=['GET', 'POST'])
@login_required
def delete(content):
    if request.method == 'POST':
        try:
            print("Delete Pressed: {}".format(content))
            post_delete = Posts.query.filter_by(content=content).all()
            print("Query successful! {}".format(post_delete[0].id))
            Posts.query.filter_by(id=post_delete[0].id).delete()
            print("Session.remove worked.")
            db.session.commit()
            print("successfully removed from db")
        except:
            pass
        if post_delete == None:
            print("Query did not work.")
        else:
            print("{}, {}, {}".format(post_delete[0].id, post_delete[0].username, post_delete[0].content))
    print("GET redirect")
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', 404)

###--------------------------
# Main
###--------------------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
