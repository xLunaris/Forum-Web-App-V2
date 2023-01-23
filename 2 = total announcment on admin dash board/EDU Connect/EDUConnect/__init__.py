from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from os import path

from EDUConnect import admin



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = "hellovialli"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .models import User, Post, Comment
    create_database(app)


    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from EDUConnect.announcements.routes import announcements
    from EDUConnect.users.routes import users
    from EDUConnect.posts.routes import posts
    from EDUConnect.admin.routes import admin
    from EDUConnect.main.routes import main
    from EDUConnect.collector.routes import collector
    from EDUConnect.errors.handlers import errors

    app.register_blueprint(announcements)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(admin)
    app.register_blueprint(collector)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Database Generated')