from flask import Flask, request, redirect, render_template, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = '1234567'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body =  db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_date = db.Column(db.DateTime)
    username = db.Column(db.String(25))

    def __init__(self, title, body, owner_id, username):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        blog_date = datetime.utcnow()
        self.username = username
        self.blog_date = blog_date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def logged_in():
    logged_in = None
    logged_in = request.cookies.get('logged_in')
    if logged_in == None:
        result = False
    else:
        result = True

    return result

@app.before_request
def require_login():
    logged_in()
    allowed_routes = ['login', 'signup', 'index', 'blog', 'single_blog']
    if request.endpoint not in allowed_routes and (not logged_in()):
        return redirect('/login')

@app.route('/logout')
def logout():
    logged_in()
    del session['username']
    response = make_response(redirect('/'))
    response.set_cookie('logged_in', expires=0)
    return response

@app.route('/',methods=['GET', 'POST'])
def index():
    logged_in()
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET','POST']) 

def login():

    if logged_in():
        return render_template('loggedIn.html')

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''
        error = True

        if username and user.password == password:
            session['username'] = username
            flash('You are logged in!')
            url = '/newpost'
            response = make_response(redirect(url))
            response.set_cookie('logged_in', username, max_age=120)

            return response

        elif user == '':
            username_error = "You must fill in all fields"
            username = ''
            error = True

        elif not user:
            username_error = "Username does not exist"
            username = ''
            error = True

        if password == '':
            password_error = "Password must not be blank"
            password = ''
            error = True

        elif user and user.password != password:
            flash('Incorrect Username or Password')

        if error:
            return render_template("login.html", username=username, username_error=username_error, 
                    password_error=password_error)

    return render_template('login.html')
            

@app.route('/signup', methods=['GET', 'POST'])  
def signup():

    logged_in()

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify-password']
        user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''
        verify_password_error = ''
        error = False

        username_db_id = User.query.filter_by(username=username).count()

        if username_db_id > 0:
            username_error = "Username already exists"
            error = True
            
        elif username == '' or  len(username) < 3 or len(username) > 20:
            username_error = "Invalid Username"
            error = True


        if password == '' or len(password) < 3 or len(password) > 20:
            password_error = "Invalid Password"
            error = True

        if password != verify_password:
            verify_password_error = "Passwords do not match"
            error = True

        if error:
            return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, 
                verify_password_error=verify_password_error)
                
        
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        session['username'] = username
        url = '/newpost'
        response = make_response(redirect(url))
        response.set_cookie('logged_in', username, max_age=120)

        return response


@app.route('/blog', methods=['GET'])
def blog():
    logged_in()
    blog = Blog.query.all()
    user = User.query.all()

    if request.args.get('user') == None:
        blog = Blog.query.all()
        print(blog)
        return render_template('blog.html', title='blog posts', blogs=blog)
    
    else:
        blog_id = request.args.get('user')
        blog_entry = Blog.query.filter_by(owner_id=blog_id).first()
        
        if blog_entry == None:
            return render_template('blog.html', title='Your Blog', blog=blog, user=user)
        else:

            owner_id = blog_entry.owner_id
            user = User.query.get(owner_id)
            blog = Blog.query.filter_by(owner_id=blog_id).all()

        return render_template('singleUser.html', title='Your Blog', blog=blog, user=user)

    return render_template('blog.html', blog=blog, user=user)

@app.route('/singleBlog', methods=['GET'])
def single_blog():
    logged_in()
    blog_id = request.args.get('id')
    blog_entry = Blog.query.get(blog_id)
    owner_id = blog_entry.owner_id
    user = User.query.get(owner_id)

    return render_template('singleBlog.html', id=blog_id, blog=blog_entry, user=owner_id, username=user.username)

    
@app.route('/newpost', methods=['POST', 'GET']) 
def newpost():
    logged_in()

    title_error = ''
    body_error = ''
    error = False

    if request.method == 'GET':
        return render_template('newpost.html', title="Add a blog entry")

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        blog_date = datetime.now()
        owner_id = User.query.filter_by(username=session['username']).first().id

    if not title and not body:
        title_error = "Please add a title"
        body_error = "Please add a body"
        error = True

    if body == '':
        title = request.form['title']
        body_error = 'Blogs cannot be empty.'
        error = True

    if title == '':
        body = request.form['body']
        title_error = 'Blogs must have a title.'
        error = True

    if error:    
        return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)
    
    else:
        blog = Blog(title, body, owner_id, session['username'])
        db.session.add(blog)
        db.session.commit()
        id = str(blog.id)
        return redirect('/singleBlog?id='+ id)

    return render_template('newpost.html')







if __name__ == '__main__':
    app.run()

