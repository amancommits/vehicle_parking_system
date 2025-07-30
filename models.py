from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), default='user')
    location = db.Column(db.String(), unique=False, nullable=True)
    vehicle_number = db.Column(db.String(), unique=True,nullable=True)
    pin = db.Column(db.Integer,nullable=True)
    posts = db.relationship('Release', backref='user', lazy=True)


class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location = db.Column(db.String(), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(), unique=True, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    maximum_spots = db.Column(db.Integer)
    spots = db.relationship('Spot', backref='lot', lazy=True)


class Spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    spot_number = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String(), default='available')
    user = db.relationship('User', backref='spots')
    releases = db.relationship('Release', backref='spot', lazy=True)

class Release(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parked_at = db.Column(db.DateTime, server_default=db.func.now())
    released_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    cost = db.Column(db.Integer, nullable=False)   

    