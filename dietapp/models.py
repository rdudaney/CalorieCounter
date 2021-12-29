from dietapp import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default='default.jpg')
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    last_login = db.Column(db.DateTime)
    obsolete = db.Column(db.Boolean, nullable = False, default=False)

    ingredients = db.relationship('Ingredients', backref='author',lazy=True)
    meals = db.relationship('Meals', backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}', '{self.date_created}')"


class Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    brand = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    date_used = db.Column(db.DateTime)
    favorite = db.Column(db.Boolean, nullable = False, default=False)
    obsolete = db.Column(db.Boolean, nullable = False, default=False)

    protein = db.Column(db.Float, default = 0)
    carbs = db.Column(db.Float, default = 0)
    fat = db.Column(db.Float, default = 0)
    calories = db.Column(db.Float,default=0, nullable = False)

    serv_weight = db.Column(db.Float)
    serv_volume = db.Column(db.Float)
    serv_count = db.Column(db.Float)

    weight_unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    volume_unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    count_unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    

    def __repr__(self):
        return f"Ingr('{self.id}','{self.brand}', '{self.name}' )"
        

class Units(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    conversion = db.Column(db.Float, nullable = False)
    obsolete = db.Column(db.Boolean, nullable = False, default=False)

    unit_type_id = db.Column(db.Integer, db.ForeignKey('unit_type.id'), nullable = False)

    unit_type = db.relationship('UnitType', backref='units',lazy=True)

    def __repr__(self):
        return f"Units('{self.id}', '{self.name}', '{self.unit_type_id}' )"

class UnitType(db.Model):
    #__tablename__ = 'example'
    id = db.Column(db.Integer, primary_key = True)
    typ = db.Column(db.String(100), nullable = False)

    def __repr__(self):
        return f"UnitType('{self.id}', '{self.typ}' )"


class MealIngredients(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable = False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable = False)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable = False)
    serv = db.Column(db.Float, nullable = False)

    ingredient = db.relationship('Ingredients', backref='ingredient',lazy=True)


class Meals(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    date_used = db.Column(db.DateTime)
    favorite = db.Column(db.Boolean, nullable = False, default=False)
    obsolete = db.Column(db.Boolean, nullable = False, default=False)

    protein = db.Column(db.Float, default = 0)
    carbs = db.Column(db.Float, default = 0)
    fat = db.Column(db.Float, default = 0)
    calories = db.Column(db.Float,default=0)

    serv_weight = db.Column(db.Float)
    serv_volume = db.Column(db.Float)
    serv_count = db.Column(db.Float)

    weight_unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    volume_unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    count_unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))

    recipe = db.Column(db.String(100))
    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)



    meal_ingredients = db.relationship('MealIngredients', backref='meals',lazy=True)

    



#https://stackoverflow.com/questions/53900595/sqlalchemy-error-on-creating-multiple-foreign-key-to-one-table

#class CalorieGoals:
    #int id
    #int user_id
    #int calories
    #int date_added

#class Unit_Conversion:






#class Day: 