import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata) # type: ignore

# def create_app(): 

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
if os.environ.get("FLASK_ENV") == "production":
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MYSQL_PRIVATE_URL"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MYSQL_URL"]
    # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["AWS_DATABASE_URL"]

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database Plugin
with app.app_context():
    from .models import *
db.init_app(app)
migrate = Migrate(app, db)