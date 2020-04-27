from datetime import datetime
from flaskDemo import db, login_manager
from flask_login import UserMixin
from functools import partial
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Author(db.Model):
    __table__ = db.Model.metadata.tables['author']

class Journal(db.Model):
    __table__ = db.Model.metadata.tables['journal']

class Organism(db.Model):
    __table__ = db.Model.metadata.tables['organism']

class Publication(db.Model):
    __table__ = db.Model.metadata.tables['publication']

class School(db.Model):
    __table__ = db.Model.metadata.tables['school']

class Sequence(db.Model):
    __table__ = db.Model.metadata.tables['sequence']

class Author_Publications(db.Model):
    __table__ = db.Model.metadata.tables['author_publications']

class Seq_Type(db.Model):
    __table__ = db.Model.metadata.tables['seq_type']