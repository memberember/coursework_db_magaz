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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
