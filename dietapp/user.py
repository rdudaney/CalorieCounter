from dietapp.models import User
from dietapp import app, db, bcrypt

class UserClass:
    def __init__(self, form):
        self.username = form.username.data
        self.email = form.email.data
        self.hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

    def addUser(self):
        new_user = User(username = self.username, email=self.email, password=self.hashed_pw)
        db.session.add(new_user)
        db.session.commit()