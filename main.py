from flask import Flask, render_template, request, json, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlighter import SQLighter
import time
import utils as ut

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moodleDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# инициализируем соединение с БД
dblite = SQLighter('moodleDB')


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Integer, nullable=2)
    fio = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id}'


class DegreeProgramm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.faculty_id} {self.name}'


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.faculty_id} {self.name}'


class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.name}'


class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    teacher_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'{self.id} {self.teacher_id} {self.name}'


@app.route('/')
def index():
    if request.method == "POST":
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        # костыль
        items = dblite.get_user_auth(login=email, password=password)
        if len(items) != 0:
            print(email, password, items[0])
            return redirect('users')
        else:
            print("Такого юзера нету")
            return 'Получилась ошибка'
    else:
        return render_template('auth.html'
                               # ,data=items
                               )


@app.route('/users')
def users():
    items = Users.query.order_by(Users.id).all()
    # print(items[0].fio)
    # if request.method == "POST":
    #     user_id = request.form['user_id']
    #     user_type = ut.get_user_type(request.form['user_type'])
    #     fio = request.form['fio']
    #     print(user_id, fio, user_type)
    #
    #     user = Users.query.get(user_id)
    #     user.fio = fio
    #     user.type = user_type
    #     db.session.add(user)
    #     db.session.commit()
    #
    return render_template('users.html', data=items)


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


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    # if request.method == "POST":
    #     fio = request.form['fio']
    #     coming_or_leave = False
    #     print(request.form)
    #     if request.form.get('coming_or_leave') != None:
    #         coming_or_leave = True
    #
    #     visit = Visit_list(fio=fio, coming_or_leave=coming_or_leave)
    #     try:
    #         db.session.add(visit)
    #         db.session.commit()
    #         return redirect('/')
    #     except:
    #         return 'Получилась ошибка'
    # else:
    #     return render_template('create.html')
    return render_template('create.html')


if __name__ == "__main__":
    # app.run(debug=True,
    #         # host='0.0.0.0'
    #         )
    items = DegreeProgramm.query.order_by(DegreeProgramm.id).all()
    print(items)
    items = Faculty.query.order_by(Faculty.id).all()
    print(items)
    items = Discipline.query.order_by(Discipline.id).all()
    print(items)
    items = Department.query.order_by(Department.id).all()
    print(items)
