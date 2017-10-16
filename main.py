from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


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

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/')
def index():

    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/login', methods=['GET','POST']) # -- validation is not functioning
def login():
    password_error = "Not a valid password"

    if request.method == 'POST':

        if not username and not password:
            flash('Please fill out all fields')
            return redirect('/login')

        if request.args:
            username = request.args.get("username")
            password = request.args.get("password")

            return redirect('/newpost?id=' + str(user.id))
        else:
            return render_template('login.html', title='Login', password_error=password_error)
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])  # -- username and password still isnt hitting the db
def signup():
    verify_password_error = "Passwords do not match"
    
    return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username and not password and not verify_password: # -- validation is not functioning
            flash("Please fill out all fields")
            return redirect('/signup')

        if password != verify_password:
            return render_template('signup.html',username=username, verify_password_error=verify_password_error)
        else:    
            user = User(username,password) 
            db.session.add(user)
            db.session.commit()
            return redirect('/blog?id=' + str(blog.id))


@app.route('/blog', methods=['GET'])
def blog():

  if request.args:
    id = request.args.get("id")
    blog = Blog.query.get(id)

    return render_template('singleUser.html', title="Build A Blog", blog=blog)

  else:
    blogs = Blog.query.all()

    return render_template('blog.html', blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title and not body:
            flash("Please fill out all fields.")
            return redirect('/newpost')

        if body == '':
            title = request.form['title']
            flash('Please fill out all fields.')
            return render_template('newpost.html', title=title)

        if title == '':
            body = request.form['body']
            flash('Please fill out all fields.')
            return render_template('newpost.html', body=body)

        

        else:
             blog = Blog(title, body) 
             db.session.add(blog)
             db.session.commit()
             return redirect('/blog?id=' + str(blog.id))

    return render_template('newpost.html')



if __name__ == '__main__':
    app.run()

