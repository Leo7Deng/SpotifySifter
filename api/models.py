from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from app import app
db.init_app(app)

class Skipped(db.Model):
  __tablename__ = 'skipped'
  id = db.Column(db.Integer, primary_key=True)
  skipped_count = db.Column(db.Integer)
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
  playlist_id = db.Column(db.String(120), db.ForeignKey('playlist.id'))

class Track(db.Model):
  __tablename__ = 'track'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  playlist_id = db.Column(db.String(120), db.ForeignKey('playlist.id'))

class Playlist(db.Model):
  __tablename__ = 'playlist'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  # skipped_once = db.relationship('Track', secondary='skipped_once', backref=db.backref('playlist_skipped_once', lazy='dynamic'))
  # skipped_twice = db.relationship('Track', secondary='skipped_twice', backref=db.backref('playlist_skipped_twice', lazy='dynamic'))
  user_id = db.Column(db.String, db.ForeignKey('user.email'))

class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120))

class PrevQueue(db.Model):
  __tablename__ = 'prev_queue'
  id = db.Column(db.Integer, primary_key=True)
  track_id = db.Column(db.String(120), db.ForeignKey('track.id'))
  queue_index = db.Column(db.Integer)
  user_id = db.Column(db.String(120), db.ForeignKey('user.email'))