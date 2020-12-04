from flask import render_template, request, json, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from sweater.models import User, Department, Discipline, DegreeProgramm, Faculty
from sweater import app, db
from sweater.utils import get_user_type


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('inputEmail')
    password = request.form.get('inputPassword')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')
            if next_page != None:
                return redirect(next_page)
            return redirect(url_for('about'))

        else:
            flash('Логин и пароль не верные')
    return render_template('login_page.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('inputEmail')
    password = request.form.get('inputPassword')
    password2 = request.form.get('inputPassword2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, type=2)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))
    return render_template('register_page.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


# главная страница
@login_required
@app.route('/')
def index():
    return render_template('login_page.html'
                           # ,data=items
                           )


# страница пользователей
@app.route('/users')
@login_required
def users():
    items = User.query.order_by(User.id).all()
    return render_template('users.html', data=items)


# страница направлений
@app.route('/degree_programms')
@login_required
def degree_programms():
    items = DegreeProgramm.query.order_by(DegreeProgramm.id).all()
    return render_template('degreeProgramms.html', data=items)


# страница кафедр
@app.route('/departments')
@login_required
def departments():
    items = Department.query.order_by(Department.id).all()
    return render_template('departments.html', data=items)


# страница факультетов
@app.route('/faculties')
@login_required
def faculties():
    items = Faculty.query.order_by(Faculty.id).all()
    return render_template('faculties.html', data=items)


# страница дисциплин
@app.route('/disciplines')
@login_required
def disciplines():
    items = Discipline.query.order_by(Discipline.id).all()
    return render_template('disciplines.html', data=items)


# адрес для ajax запроса
@app.route('/process', methods=['GET', 'POST'])
@login_required
def process():
    if len(request.form) > 0:
        print("request1 ", request.form)
        fio = request.form['fio'];
        print("process", fio)
        return json.dumps({'len': len(fio)})
    return 'Error'

    # user = Users.query.get(id)
    # user.l = 'ww@gmail.com'
    # # db.session.add(user)
    # # db.session.commit()


# страница "О нас"
@app.route('/about')
@login_required
def about():
    current = current_user
    current.type = get_user_type(current_user.type)
    return render_template('about.html', data=current)


# страница создания пользователя
@app.route('/createUser', methods=['POST', 'GET'])
@login_required
def create_user():
    # проверка запроса
    if request.method == "POST":

        # считывание данных с формы
        login = request.form["login"]
        password = request.form["password"]
        fio = request.form["fio"]
        type = request.form["type"]

        # создание объекта User
        user = User(login=login, password=password, fio=fio, type=type)

        # подключение к базе данных и добавления пользователя
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/users')
        except:
            return 'Получилась ошибка'
    else:
        return render_template('createUser.html')
    return render_template('createUser.html')


# страница создания факультета
@app.route('/createFaculty', methods=['POST', 'GET'])
@login_required
def create_faculty():
    # проверка запроса
    if request.method == "POST":

        # считывание данных с формы
        name = request.form["name"]

        # создание объекта Faculty
        faculty = Faculty(name=name)

        # подключение к базе данных и добавления факультета
        try:
            db.session.add(faculty)
            db.session.commit()
            return redirect('/faculties')
        except:
            return 'Получилась ошибка'
    else:
        return render_template('createFaculty.html')
    return render_template('createFaculty.html')


# страница создания дисциплины
@app.route('/createDiscipline', methods=['POST', 'GET'])
@login_required
def create_discipline():
    teachers = User.query.filter_by(type=2).order_by(User.id).all()

    # проверка запроса
    if request.method == "POST":

        # считывание данных с формы
        name = request.form["name"]
        teacher_id = request.form["teacher_id"]

        # создание объекта Faculty
        discipline = Discipline(name=name, teacher_id=teacher_id)

        # подключение к базе данных и добавления дисциплины
        try:
            db.session.add(discipline)
            db.session.commit()
            return redirect('/faculties')
        except:
            return 'Получилась ошибка'
    else:
        return render_template('createDiscipline.html', data=teachers)
    return render_template('createDiscipline.html', data=teachers)


# страница создания кафедры
@app.route('/createDepartment', methods=['POST', 'GET'])
@login_required
def create_department():
    faculty_list = Faculty.query.order_by(Faculty.id).all()

    # проверка запроса
    if request.method == "POST":

        # считывание данных с формы
        name = request.form["name"]
        faculty_id = request.form["faculty_id"]

        # создание объекта Faculty
        department = Department(name=name, faculty_id=faculty_id)

        # подключение к базе данных и добавление кафедры
        try:
            db.session.add(department)
            db.session.commit()
            return redirect('/departments')
        except:
            return 'Получилась ошибка'
    else:
        return render_template('createDepartment.html', data=faculty_list)
    return render_template('createDepartment.html', data=faculty_list)


# страница создания факультета
@app.route('/createDegreeProgramm', methods=['POST', 'GET'])
@login_required
def create_degree_programm():
    faculty_list = Faculty.query.order_by(Faculty.id).all()

    # проверка запроса
    if request.method == "POST":

        # считывание данных с формы
        name = request.form["name"]
        faculty_id = request.form["faculty_id"]

        # создание объекта Faculty
        degree_programm = DegreeProgramm(name=name, faculty_id=faculty_id)

        # подключение к базе данных и добавление направления
        try:
            db.session.add(degree_programm)
            db.session.commit()
            return redirect('/degree_programms')
        except:
            return 'Получилась ошибка'
    else:
        return render_template('createDegreeProgramm.html', data=faculty_list)
    return render_template('createDegreeProgramm.html', data=faculty_list)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response
