from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# подключаем фласк и sqlalchemy для работы с бд
app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///magazDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from sweater import models, routes

db.create_all()
