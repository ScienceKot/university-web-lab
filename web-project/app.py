from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for,flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user

app = Flask(__name__, template_folder = 'templates')
app.static_folder = 'static'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "super_secret_key"
db = SQLAlchemy(app)
auth = Blueprint('auth', __name__)

login_manager = LoginManager()

migrate=Migrate(app,db)
manager = Manager(app)

login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=False)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=False)
    role = db.Column(db.Integer)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    download_link = db.Column(db.String(255), unique=True)
    game = db.Column(db.Boolean, default=False, nullable=False)

@app.route('/', methods=['GET'])
def index():
    list_products = Content.query.all()
    return render_template('index.html', list_products = list_products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user_exists = User.query.filter_by(email = email).first()

        if user_exists:
            return render_template('user_already_exists.html')

        new_user = User(username=username, email=email, password=password, role=role)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        id = User.query.filter_by(email=email).first().id
        return redirect(url_for('profile', id=id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            return redirect(url_for('user_not_exist', email=email))
        else:
            if password == user.password:
                login_user(user)
                return redirect(url_for('profile'))
            else:
                return redirect(url_for('wrong_pass'))

@app.route('/add-content', methods=['GET', 'POST'])
def add_content():
    if request.method == 'GET':
        return render_template('add_content.html')
    else:
        name = request.form.get('name')
        download_link = request.form.get('download_link')
        game = request.form.get('game')
        game = True if game == 'on' else False

        new_content = Content(name = name, download_link = download_link, game = game)

        db.session.add(new_content)
        db.session.commit()
        return redirect(url_for('add_content'))

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@app.route('/product/<id>', methods=['GET'])
def product(id):
    product = Content.query.filter_by(id = id).first()
    return render_template('product.html', product = product)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    if session.get('was_once_logged_in'):
        # prevent flashing automatically logged out message
        del session['was_once_logged_in']
    flash('You have successfully logged yourself out.')
    return redirect('/login')

@app.route('/user_not_exist', methods=['GET'])
def user_not_exist():
    return render_template('user_not_exist.html')

@app.route('/wrong-password', methods=['GET'])
def wrong_pass():
    return render_template('wrong_pass.html')

@app.route('/edit', methods=['GET'])
@login_required
def edit():
    products = Content.query.all()
    return render_template('edit.html', products = products)

@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if request.method == 'GET':
        product = Content.query.filter_by(id = id).first()
        return render_template('edit-product.html', product = product)
    else:
        name = request.form.get('name')
        download_link = request.form.get('download_link')
        game = request.form.get('game')
        game = True if game == 'on' else False

        product = Content.query.filter_by(id = id).first()

        product.name = name
        product.download_link = download_link
        product.game = game

        db.session.commit()

        return redirect(url_for('product', id = id))

app.run()