from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
db.init_app(app)

class Track(db.Model):
  __tablename__ = 'track'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  playlist = db.Column(db.String(120), db.ForeignKey('playlist.id'))

class Playlist(db.Model):
  __tablename__ = 'playlist'
  playlist_id = db.Column(db.String(120), primary_key=True)
  name = db.Column(db.String(120))
  skipped_once = db.Column(Track)
  skipped_twice = db.Column(Track)
  user = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
  __tablename__ = 'user'
  email = db.Column(db.String(120), primary_key=True)
  selected_playlists = db.Column(Playlist)
  prev_queue = db.Column(Track)
