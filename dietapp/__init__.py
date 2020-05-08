#https://www.youtube.com/watch?v=MwZwr5Tvyxo&t=2s
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

file1 = open('secretkey.txt')
app.config['SECRET_KEY'] = file1.readlines()[0]
#print(app.config['SECRET_KEY'])
#import secrets
#secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#from dietapp import db
#db.create_all()
#from dietapp.models import User, Post
#user_1 = User(username = 'Rohan', email = 'rohan.dudaney@gmail.com', password = 'password')
#db.session.add(user_1)
#user_2 = User(username = 'Juhee', email = 'juheehy@hotmail.com', password = 'password')
#db.session.add(user_2)
#db.session.commit()
#User.query.all()
#User.query.first()
#User.query.filter_by(username='Rohan').all()
#db.drop_all()


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from dietapp import routes

