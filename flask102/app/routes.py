from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import select, func
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
import mysql.connector

conn = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='MicroBlogData2')

cursor = conn.cursor()


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'Kenny'},
            'body': "Japan's SAKURA is beautiful!"
        },
        {
            'author': {'username': 'Mandy'},
            'body': "My baby is quite, right?"
        }
    ]
    return render_template(template_name_or_list='index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        input_name = form.username.data
        user = db.session.scalar(select(User).where(
            User.username == {input_name}
        ))
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect username or password')
            print('Incorrect username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template(template_name_or_list='login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        if password != confirmPassword:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        sql = "INSERT INTO user (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, hashed_password)
        cursor.execute(sql, val)
        # 提交事務
        conn.commit()
        # 關閉游標和連接
        cursor.close()
        conn.close()    
        flash('Registration successful')
        return redirect(url_for('login'))
    

    return render_template('register.html', title='Register')


@app.route('/user/<username>')
@login_required
def user(username):
    query = select(User).where(
        func.lower(User.username) == {username}
    )
    user = db.first_or_404(query)
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)