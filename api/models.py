from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)

class SkippedOnce(db.Model):
  __tablename__ = 'skipped_once'
  id = db.Column(db.Integer, primary_key=True)
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
  playlist_id = db.Column(db.String(120), db.ForeignKey('playlist.id'))

class SkippedTwice(db.Model):
  __tablename__ = 'skipped_twice'
  id = db.Column(db.Integer, primary_key=True)
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