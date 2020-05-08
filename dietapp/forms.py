from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, SelectField, FieldList, FormField
from wtforms.validators import InputRequired, InputRequired, Length, Email, EqualTo, ValidationError, Optional
from dietapp.models import User
from dietapp.models import Units

class RegistrationForm(FlaskForm):
    username = StringField('Username',
        validators =[InputRequired(), Length(min=2,max =20)])
    email = StringField('Email', validators =[InputRequired(), Email()])
    password = PasswordField('Password', validators =[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators =[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')



class LoginForm(FlaskForm):
    email = StringField('Email', validators =[InputRequired(), Email()])
    password = PasswordField('Password', validators =[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class IngredientForm(FlaskForm):
    brand = StringField('Brand')
    name = StringField('Name', validators =[InputRequired()])

    fat = DecimalField('Fat (g)')
    carbs = DecimalField('Carbs (g)')
    protein = DecimalField('Protein (g)')
    calories = DecimalField('Calories', validators =[InputRequired()])

    serv_weight = DecimalField('Serving Size by Weight', validators =[Optional()])
    serv_volume = DecimalField('Serving Size by Volume', validators =[Optional()])
    serv_count = DecimalField('Serving Size by Count/Servings', validators =[Optional()])

    drop_weight = SelectField('Unit Weight', coerce=int)
    drop_volume = SelectField('Unit Volume', coerce=int)
    drop_count = SelectField('Unit Count', coerce=int)

    submit = SubmitField('Submit')


    #https://stackoverflow.com/questions/29703979/flask-conditional-validation-on-multiple-form-fields
    def validate(self):
        if not super(IngredientForm, self).validate():
            return False

        if self.serv_weight.data is None and self.serv_volume.data is None and self.serv_count.data is None:
            msg = 'Must enter at least one serving size'
            self.serv_weight.errors.append(msg)
            self.serv_volume.errors.append(msg)
            self.serv_count.errors.append(msg)
            return False
        return True




def getUnits(ingredient):
    units = []
    if(ingredient.serv_weight is not None):
        units += Units.query.filter_by(unit_type_id=1).with_entities(Units.id, Units.name).all()
    if(ingredient.serv_volume is not None):
        units += Units.query.filter_by(unit_type_id=2).with_entities(Units.id, Units.name).all()
    if(ingredient.serv_count is not None):
        units += Units.query.filter_by(id =ingredient.count_unit_id).with_entities(Units.id, Units.name).all()

    return units


def MealForm(meal):
    class F(FlaskForm):
        name = StringField('Title',validators =[InputRequired()])


    for i,mi in enumerate(meal.meal_ingredients):
        ingredient = meal.meal_ingredients[i].ingredient
        units = getUnits(ingredient)

        setattr(F,'amount%d' % i, DecimalField('Amount%d' % i))
        setattr(F,'unit%d' % i, SelectField('Unit%d' % i, coerce=int,choices=units))
        

    d = F()
    d.name.data = meal.name
    for i,mi in enumerate(meal.meal_ingredients):
        d['amount%d' % i].data=mi.serv
        d['unit%d' % i].data=mi.unit_id

    return d