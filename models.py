from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Show(db.Model):
    __tablename__ = 'Show'

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    genres = db.Column(db.String(255))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(255))
    website_link = db.Column(db.String(255))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref = 'venue')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    genres = db.Column(db.String(255))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(255))
    website_link = db.Column(db.String(255))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref = 'artist')
