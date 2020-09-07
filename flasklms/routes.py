import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flasklms import app, db, bcrypt, mail
from flasklms.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from flasklms.models import User, ClassRoom
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        if current_user.isTeacher:
            page = request.args.get('page', 1, type=int)
            classrooms=ClassRoom.query.filter_by(user_id=current_user.id).order_by(ClassRoom.date_posted.desc()).paginate(page=page, per_page=5)
            return render_template('home.html', classrooms=classrooms)
        else:
            page = request.args.get('page', 1, type=int)
            classrooms = ClassRoom.query.order_by(ClassRoom.date_posted.desc()).paginate(page=page, per_page=5)
            return render_template('home.html', classrooms=classrooms)
    else:
        page = request.args.get('page', 1, type=int)
        classrooms = ClassRoom.query.order_by(ClassRoom.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', classrooms=classrooms)

@app.route("/classroomName")
def classroomName():
    if current_user.is_authenticated:
        if current_user.isTeacher:
            page = request.args.get('page', 1, type=int)
            classrooms=ClassRoom.query.filter_by(user_id=current_user.id).order_by(ClassRoom.classroomName.desc()).paginate(page=page, per_page=5)
            return render_template('home.html', classrooms=classrooms)
        else:
            page = request.args.get('page', 1, type=int)
            classrooms = ClassRoom.query.order_by(ClassRoom.classroomName.desc()).paginate(page=page, per_page=5)
            return render_template('home.html', classrooms=classrooms)
    else:
        page = request.args.get('page', 1, type=int)
        classrooms = ClassRoom.query.order_by(ClassRoom.classroomName.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', classrooms=classrooms)

@app.route("/subject")
def subject():
    if current_user.is_authenticated:
        if current_user.isTeacher:
            page = request.args.get('page', 1, type=int)
            classrooms=ClassRoom.query.filter_by(user_id=current_user.id).order_by(ClassRoom.subject.desc()).paginate(page=page, per_page=5)
            return render_template('home.html', classrooms=classrooms)
        else:
            page = request.args.get('page', 1, type=int)
            classrooms = ClassRoom.query.order_by(ClassRoom.subject.desc()).paginate(page=page, per_page=5)
            return render_template('home.html', classrooms=classrooms)
    else:
        page = request.args.get('page', 1, type=int)
        classrooms = ClassRoom.query.order_by(ClassRoom.subject.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', classrooms=classrooms)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, isTeacher=form.isTeacher.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else: 
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        classroom = ClassRoom(classroomName=form.classroomName.data, subject=form.subject.data , time=form.time.data ,daysOfClasses=form.daysOfClasses.data ,  content=form.content.data, teacher=current_user)
        db.session.add(classroom)
        db.session.commit()
        flash('Your Classroom has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Classroom',
                           form=form, legend='New Classroom')


@app.route("/post/<int:post_id>")
def post(post_id):
    classroom = ClassRoom.query.get_or_404(post_id)
    return render_template('post.html', title=classroom.classroomName, classroom=classroom)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    classroom = ClassRoom.query.get_or_404(post_id)
    if classroom.teacher != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        classroom.classroomName = form.classroomName.data
        classroom.content = form.content.data
        classroom.subject=form.subject.data
        classroom.daysOfClasses=form.daysOfClasses.data
        classroom.time=form.time.data
        db.session.commit()
        flash('Your classroom has been updated!', 'success')
        return redirect(url_for('post', post_id=classroom.id))
    elif request.method == 'GET':
        form.classroomName.data = classroom.classroomName
        form.content.data = classroom.content
        form.subject.data=classroom.subject
        form.time.data=classroom.time
        form.daysOfClasses.data=classroom.daysOfClasses
    return render_template('create_post.html', title='Update Classroom',
                           form=form, legend='Update Classroom')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    classroom = ClassRoom.query.get_or_404(post_id)
    if classroom.teacher != current_user:
        abort(403)
    db.session.delete(classroom)
    db.session.commit()
    flash('Your classroom has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    classroom = ClassRoom.query.filter_by(teacher=user).order_by(ClassRoom.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', classrooms=classroom, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)