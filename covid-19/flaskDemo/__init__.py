from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hiQy1QG1kErgfGajdI7ABw'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://brianho:tingting3@127.0.0.1:8889/covid_19'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskDemo import routes
from flaskDemo import models

models.db.create_all()
