from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import ResetPasswordRequestForm, ResetPasswordForm, LoginForm, RegistrationForm, CheckPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
import time
from app.email import send_password_reset_email

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = CheckPasswordForm()
    password_checker = None
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            password_checker = True
        else:
            password_checker = False
    return render_template('index.html', title='Home Page', form=form, password_checker=password_checker)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/loading/data')
def loading_data():
    time.sleep(5)
    data = {
        'name': 'Max',
        'age': 22
    }
    return render_template('loading_finished.html', data=data)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))

    return render_template('reset_password_request.html', title="Reset Password", form=form)


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

    return render_template('reset_password_request.html', form=form)
