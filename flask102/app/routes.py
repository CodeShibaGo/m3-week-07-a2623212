from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import select, func
from app import app, db
from app.forms import EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
import sqlalchemy as sa
from app.models import User, Post
from urllib.parse import urlsplit
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app.email import send_password_reset_email

conn = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='MicroBlogData2')

cursor = conn.cursor()


@app.before_request
def before_request():
    print('before request')
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


# Index
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    print('Index!')
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is shared')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('rememberMe')
        # From Database get the username and password
        query = ("SELECT password, email, id FROM user WHERE username = %s ")
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result is None:
            print('Incorrect username or password')
            return redirect(url_for('login'))

        hash_password = result[0]
        email = result[1]
        id = result[2]

        if not check_password_hash(hash_password, password):
            print('Incorrect username or password')
            return redirect(url_for('login'))
       
        user = User.query.filter_by(username=username).first()
        print(user)
        if user:
            login_user(user, remember=True)
            print('login success')
            print(current_user.is_active)
            print(current_user.is_authenticated)
            print(current_user.is_anonymous)
            print(current_user.get_id())
            # 重定向到 “next” 頁面
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template(template_name_or_list='login.html', title='Login')


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
        # # 關閉游標和連接
        # cursor.close()
        # conn.close()    
        flash('Registration successful')
        return redirect(url_for('login'))
    

    return render_template('register.html', title='Register')


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


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


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

# All posts
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

# Reset Password
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email to get the hint!')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)