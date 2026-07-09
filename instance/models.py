from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Restaurant(db.Model):

    __tablename__ = "restaurant"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class NGO(db.Model):

    __tablename__ = "ngo"

    id = db.Column(db.Integer, primary_key=True)
    ngo_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class Admin(db.Model):

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class Donation(db.Model):

    __tablename__ = "donation"

    id = db.Column(db.Integer, primary_key=True)
    restaurant = db.Column(db.String(100))
    food_name = db.Column(db.String(100))
    quantity = db.Column(db.String(50))
    address = db.Column(db.String(200))
    ready_until = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Available")
    claimed_by = db.Column(db.String(100), default="")