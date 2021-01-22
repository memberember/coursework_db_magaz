from flask_login import UserMixin

from sweater import db, login_manager


# модель БД "Пользователи"
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Integer, nullable=2)
    fio = db.Column(db.String(255), nullable=True)
    sex = db.Column(db.String(255), nullable=True)
    adress = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.id} {self.fio} {self.type}'


# модель БД "Магазины"
class Magazin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='magaz', uselist=False)


# модель БД "Заказы"
class Zakaz(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(255), nullable=False)
    all_cost = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    magaztovar_id = db.Column(db.Integer, db.ForeignKey('magazinhastovar.id'), nullable=False)
    user = db.relationship('User', backref='zakaz', uselist=False)
    magazinhastovar = db.relationship('Magazinhastovar', backref='zakaz', uselist=False)


# модель БД "Товары"
class Tovar(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cvet = db.Column(db.String(255), nullable=False)
    opisanie = db.Column(db.String(255), nullable=False)
    strana = db.Column(db.String(255), nullable=False)
    razmer = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    sex = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('kategorya.id'), nullable=False)
    category = db.relationship('Kategorya', backref='tovar', uselist=False)


# модель БД "Категории"
class Kategorya(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


# модель БД "Магазин имеет товар"
class Magazinhastovar(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    magazin_id = db.Column(db.Integer, db.ForeignKey('magazin.id'), nullable=False)
    tovar_id = db.Column(db.Integer, db.ForeignKey('tovar.id'), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    magazin = db.relationship(Magazin, backref='magazinhastovar', uselist=False)
    tovar = db.relationship('Tovar', backref='magazinhastovar', uselist=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
