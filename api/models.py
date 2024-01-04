from api import db

class Skipped(db.Model):
    __tablename__ = "skipped"
    id = db.Column(db.Integer, primary_key=True)
    skipped_count = db.Column(db.Integer)
    track_id = db.Column(db.String(120))
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Playlist(db.Model):
    __tablename__ = "playlist"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    playlist_id = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    currently_playing = db.Column(db.Boolean)
    selected = db.Column(db.Boolean)
    delete_playlist = db.Column(db.String(120))

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    user_id = db.Column(db.String(120))
    profile_pic = db.Column(db.String(120))
    total_played = db.Column(db.Integer)

class PrevQueue(db.Model):
    __tablename__ = "prev_queue"
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.String(120))
    queue_index = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class OAuth(db.Model):
    __tablename__ = "oauth"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    access_token = db.Column(db.String(360))
    refresh_token = db.Column(db.String(180))
    expires_at = db.Column(db.Integer)
    user = db.relationship("User", backref=db.backref("oauth", uselist=False))
