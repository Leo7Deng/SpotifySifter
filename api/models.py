from flask_sqlalchemy import SQLAlchemy
from app_init import db
# from app import app
# db = SQLAlchemy(app, metadata=metadata)
# # db.init_app(app)
# migrate = Migrate(app, db)
# migrate.init_app(app, db, render_as_batch=True)

class Skipped(db.Model):
  __tablename__ = 'skipped'
  id = db.Column(db.Integer, primary_key=True)
  skipped_count = db.Column(db.Integer)
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
  playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))

class Track(db.Model):
  __tablename__ = 'track'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))

class Playlist(db.Model):
  __tablename__ = 'playlist'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  # skipped_once = db.relationship('Track', secondary='skipped_once', backref=db.backref('playlist_skipped_once', lazy='dynamic'))
  # skipped_twice = db.relationship('Track', secondary='skipped_twice', backref=db.backref('playlist_skipped_twice', lazy='dynamic'))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120))
  currently_listening = db.Column(db.Boolean)

class PrevQueue(db.Model):
  __tablename__ = 'prev_queue'
  id = db.Column(db.Integer, primary_key=True)
  track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
  queue_index = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class OAuth(db.Model):
  __tablename__ = 'oauth'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  access_token = db.Column(db.String(120))
  refresh_token = db.Column(db.String(120))
  expires_at = db.Column(db.Integer)
  user = db.relationship('User', backref='oauth')
