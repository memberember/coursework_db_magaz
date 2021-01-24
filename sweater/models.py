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


# модель БД "Пол"
class Sex(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


# модель БД "Статус заказа"
class OrderStatus(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


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
    user = db.relationship('User', backref='zakaz', uselist=False)
    magaztovar_id = db.Column(db.Integer, db.ForeignKey('magazinhastovar.id'), nullable=False)
    magazinhastovar = db.relationship('Magazinhastovar', backref='zakaz', uselist=False)
    status = db.Column(db.Integer, db.ForeignKey('order_status.id'), nullable=False)
    order_status = db.relationship(OrderStatus, backref='zakaz', uselist=False)


# модель БД "Товары"
class Tovar(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    opisanie = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('kategorya.id'), nullable=False)
    category = db.relationship('Kategorya', backref='tovar', uselist=False)

    cvet = db.Column(db.Integer, db.ForeignKey('color.id'), nullable=False)
    color = db.relationship('Color', backref='tovar', lazy=True)

    strana = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    country = db.relationship('Country', backref='tovar', uselist=False)

    razmer = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=False)
    size = db.relationship('Size', backref='tovar', uselist=False)

    sex = db.Column(db.Integer, db.ForeignKey('sex.id'), nullable=False)
    sex_name = db.relationship(Sex, backref='tovar', lazy=True)


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


# модель БД "Цвета"
class Color(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


# модель БД "Категория размера"
class SizeCategory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


# модель БД "Размер"
class Size(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    size_code = db.Column(db.Integer, db.ForeignKey('size_category.id'), nullable=False)
    size_category = db.relationship(SizeCategory, backref='size', lazy=True)
    name = db.Column(db.String(255), nullable=False)


# модель БД "Страны"
class Country(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
