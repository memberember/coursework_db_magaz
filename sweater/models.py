from flask_login import UserMixin

from sweater import db, login_manager


# модель БД "Пользователи"
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
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
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    name = db.Column(db.String(255), nullable=True)

    faculty = db.relationship('Faculty', backref='department', uselist=False)

    def __repr__(self):
        return f'\nid = {self.id}\tfaculty_id={self.faculty_id} name={self.name}'


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
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)

    teacher = db.relationship('Teacher', backref='discipline', uselist=False)

    def __repr__(self):
        return f'{self.id} {self.teacher_id} {self.name}'


# модель БД "Студент"
class Student(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)

    # чтобы это заработало, нужно указать какой из ключей выше является внешним ключем
    userData = db.relationship('User', backref='student', uselist=False)
    group = db.relationship('Group', backref='student', uselist=False)

    def __repr__(self):
        return f'{self.id}'


# модель БД "Группы"
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree_programm_id = db.Column(db.Integer, db.ForeignKey('degree_programm.id'))
    name = db.Column(db.String(255), nullable=True)
    disciplines = db.Column(db.String, nullable=True)

    # чтобы это заработало, нужно указать какой из ключей выше является внешним ключем
    degreeProgramm = db.relationship('DegreeProgramm', backref='group', uselist=False)

    def __repr__(self):
        return f'{self.id} {self.name}'


# модель БД "Учителя"
class Teacher(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    # чтобы это заработало, нужно указать какой из ключей выше является внешним ключем
    department = db.relationship('Department', backref='teacher', uselist=False)
    userData = db.relationship('User', backref='teacher', uselist=False)

    def __repr__(self):
        return f'{self.id}'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
