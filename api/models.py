from app import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

class SkippedOnce(db.Model):
  __tablename__ = 'skipped_once'
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'), primary_key=True)
  playlist_id = db.Column(db.String(120), db.ForeignKey('playlist.id'), primary_key=True)

class SkippedTwice(db.Model):
  __tablename__ = 'skipped_twice'
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'), primary_key=True)
  playlist_id = db.Column(db.String(120), db.ForeignKey('playlist.id'), primary_key=True)

class Track(db.Model):
  __tablename__ = 'track'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  playlist_id = db.Column(db.String(120), db.ForeignKey('playlist.id'))
  user_email = db.Column(db.String(120), db.ForeignKey('user.email'))

class Playlist(db.Model):
  __tablename__ = 'playlist'
  id = db.Column(db.String(120), primary_key=True)
  name = db.Column(db.String(120))
  skipped_once = db.relationship('Track', secondary='skipped_once', backref=db.backref('playlist_skipped_once', lazy='dynamic'))
  skipped_twice = db.relationship('Track', secondary='skipped_twice', backref=db.backref('playlist_skipped_twice', lazy='dynamic'))
  user_email = db.Column(db.Integer, db.ForeignKey('user.email'))

class User(db.Model):
  __tablename__ = 'user'
  email = db.Column(db.String(120), primary_key=True)
  selected_playlists = db.relationship('Playlist')
  prev_queue = db.relationship('Track', backref='user')
