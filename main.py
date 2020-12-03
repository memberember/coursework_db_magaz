from flask import Flask, render_template, request, json, redirect
from flask_sqlalchemy import SQLAlchemy

# подключаем фласк и sqlalchemy для работы с бд
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moodleDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# инициализируем соединение с БД
# dblite = SQLighter('moodleDB')


# модель БД "Пользователи"
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Integer, nullable=2)
    fio = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.fio} {self.type}'


# модель БД "Направления"
class DegreeProgramm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.faculty_id} {self.name}'


# модель БД "Кафедра"
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.faculty_id} {self.name}'


# модель БД "Факультет"
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.name}'


# модель БД "Дисциплина"
class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    teacher_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'{self.id} {self.teacher_id} {self.name}'


# главная страница
@app.route('/')
def index():
    return render_template('auth.html'
                           # ,data=items
                           )


# страница пользователей
@app.route('/users')
def users():
    items = Users.query.order_by(Users.id).all()
    return render_template('users.html', data=items)


# страница направлений
@app.route('/degree_programms')
def degree_programms():
    items = DegreeProgramm.query.order_by(DegreeProgramm.id).all()
    return render_template('degreeProgramms.html', data=items)


# страница кафедр
@app.route('/departments')
def departments():
    items = Department.query.order_by(Department.id).all()
    return render_template('departments.html', data=items)


# страница факультетов
@app.route('/faculties')
def faculties():
    items = Faculty.query.order_by(Faculty.id).all()
    return render_template('faculties.html', data=items)


# страница дисциплин
@app.route('/disciplines')
def disciplines():
    items = Discipline.query.order_by(Discipline.id).all()
    return render_template('disciplines.html', data=items)


# адрес для ajax запроса
@app.route('/process', methods=['GET', 'POST'])
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
def about():
    return render_template('about.html')


# страница создания пользователя
@app.route('/createUser', methods=['POST', 'GET'])
def create_user():
    # проверка запроса
    if request.method == "POST":

        # считывание данных с формы
        login = request.form["login"]
        password = request.form["password"]
        fio = request.form["fio"]
        type = request.form["type"]

        # создание объекта User
        user = Users(login=login, password=password, fio=fio, type=type)

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
def create_discipline():
    teachers = Users.query.filter_by(type=2).order_by(Users.id).all()

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


if __name__ == "__main__":
    app.run(debug=True,
            # host='0.0.0.0'
            )
