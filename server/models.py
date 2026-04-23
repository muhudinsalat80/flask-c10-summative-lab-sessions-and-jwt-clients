from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)

    notes = db.relationship("Note", backref="user", cascade="all, delete")


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")


    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
