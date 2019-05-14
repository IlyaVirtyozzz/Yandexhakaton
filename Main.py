from constant import *
from werkzeug.security import generate_password_hash

from flask import url_for, request, render_template, redirect, session
from flask_sqlalchemy import sqlalchemy
from loginform import *
from add_news import *
from database import *


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация', form=form)
    elif request.method == 'POST':
        user_name = form.username.data
        password = form.password.data

        user_model = db.session.query(User).filter_by(username=user_name).first()
        if user_model and user_model.password == password:
            session.clear()
            session['username'] = user_model.username
            session['user_id'] = user_model.id
            return redirect('/index')
        else:
            return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', title='Регистрация', form=form)
    elif request.method == 'POST':
        user_name = form.username.data
        password = form.password.data
        try:
            user = User(username=user_name,
                                       password=password, )

            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return redirect("/login")
        return redirect("/login")


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')

    news = db.session.query(Task).filter_by(student_id=session['user_id'])

    return render_template('index.html', username=session['username'],
                           news=news)


@app.route('/admins_console')
def admins_console():
    if 'user_id' not in session:
        return redirect('/index')
    if not db.session.query(Admins).filter_by(student_id=session['user_id']).first():
        return redirect('/index')
    attemp = db.session.query(Task).all()

    return render_template('admins_console.html', title='Админ', attemp=attemp)


@app.route('/edit_attemp/<int:id>')
def edit_attemp(id):
    if not db.session.query(Admins).filter_by(student_id=session['user_id']).first():
        return redirect('/index')

    a = db.session.query(Task).filter_by(id=id).first()
    if a.status:
        a.status = False
    else:
        a.status = True
    db.session.commit()
    return redirect('/admins_console')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        task = form.task.data
        content = form.content.data

        user = User.query.filter_by(username=session['username']).first()
        attempt = Task(task=task,
                                  code=content,
                                  status=False)
        user.SolutionAttempts.append(attempt)
        db.session.commit()
        return redirect("/index")

    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')

    nm = db.session.query(Task).filter_by(id=news_id).first()

    if (not db.session.query(Admins).filter_by(student_id=session['user_id']).first()) and (
    not nm.student_id == session['user_id']):
        return redirect('/index')

    db.session.delete(nm)
    db.session.commit()
    return redirect("/index")


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
