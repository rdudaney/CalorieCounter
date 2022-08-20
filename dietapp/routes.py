import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from dietapp import app, db, bcrypt
from dietapp.forms import RegistrationForm, LoginForm, IngredientForm, MealForm, create_MealForm
from dietapp.models import User, Ingredients, Units, UnitType, Meals, MealIngredients
from dietapp.user import UserClass
from dietapp.ingredient import IngredientClass
from dietapp.meal import MealClass
from dietapp.route_functions import parse_element, parse_element_wtf, fcn_save_new_from_form, fcn_update_from_form, create_ingr_list, \
    create_unit_dict, add_ingredients, delete_ingredients
from flask_login import login_user, current_user, logout_user, login_required
from collections import namedtuple


@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    str_query = "SELECT date_eaten, SUM(calories) as daily_calories, SUM(carbs) as daily_carbs, SUM(protein) as daily_protein, SUM(fat) as daily_fat FROM Meals WHERE exclude_from_daily = False AND user_id = " + str(current_user.id) + " GROUP BY date_eaten ORDER BY date_eaten DESC"
    result = db.engine.execute(str_query)
    

    s= []
    for row in result:
        d = {}
        d["date"] = row[0]
        d["calories"] = row[1]
        d["carbs"] = row[2]
        d["protein"] = row[3]
        d["fat"] = row[4]
        s.append(d)

    return render_template('home.html', title='Home', sums=s)


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = UserClass(form)
        user.addUser()
        flash(f'Account created for {user.username}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register', form = form)


@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if(user and bcrypt.check_password_hash(user.password,form.password.data)):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',title='Login', form = form)


@app.route('/ingredients', methods=['GET','POST'])
@login_required
def ingredients():
    if request.method == 'POST':
        ingredient_id_list = parse_element(request.form,'check')
        delete_ingredients(ingredient_id_list)
    ingredients = Ingredients.query.filter_by(user_id = current_user.id, obsolete = False).all()
    return render_template('ingredients.html',title='Ingredients', ingredients=ingredients)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/ingredients/new", methods=['GET','POST'])
@login_required
def new_ingredient():
    form = IngredientForm()
    
    form.drop_weight.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=1).all()]
    form.drop_volume.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=2).all()]
    form.drop_count.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=3).all()]

    if form.validate_on_submit():
        ingredient = IngredientClass(form,"form")
        ingredient.save()
        flash('Your ingredient has been added!', 'success')
        return redirect(url_for('ingredients'))
    return render_template('create_ingredient.html',title='New Ingredient', legend='Add Ingredient', form = form)


@app.route("/meals/new", methods=['GET','POST'])
@login_required
def new_meal():
    new_meal_id = fcn_save_new_from_form(None, 'NewMeal')
    return redirect(url_for('update_meal',meal_id = new_meal_id))



@app.route("/ingredients/<int:ingredient_id>/update", methods=['GET','POST'])
@login_required
def update_ingredient(ingredient_id):
    ingredient_model = Ingredients.query.get_or_404(ingredient_id)
    ingredient = IngredientClass(ingredient_model,"model")

    if current_user.id != ingredient.user_id:
        abort(403)

    form = IngredientForm()
    form.drop_weight.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=1).all()]
    form.drop_volume.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=2).all()]
    form.drop_count.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=3).all()]


    if form.validate_on_submit():
        ingredient.update_from_form(form)
        ingredient.save()
        flash('Ingredient has been updated', 'success')
        return redirect(url_for('update_ingredient',ingredient_id = ingredient.id))
    elif request.method == 'GET':
        ingredient.add_to_form(form)

    return render_template('create_ingredient.html',title='Update Ingredient',form=form, legend='Update Ingredient')


@app.route("/meals")
@login_required
def meals():
    meals = Meals.query.order_by(Meals.date_created.desc()).filter_by(user_id = current_user.id, obsolete = False).all()
    return render_template('meals.html',title='Meal', meals=meals)


@app.route("/meals/<int:meal_id>/update", methods=['GET','POST'])
@login_required
def update_meal(meal_id):

    meal = Meals.query.get_or_404(meal_id)
    if current_user != meal.author:
        abort(403)

    form = create_MealForm(meal)
    
    form.drop_weight.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=1).all()]
    form.drop_volume.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=2).all()]
    form.drop_count.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=3).all()]

    ingr_list = create_ingr_list(meal)
    unit_dict = create_unit_dict()

    if form.validate_on_submit():
        print("Total Name: " + str(form.name.data))
        print("Total Fat: " + str(form.total_fat.data))
        print("Total Carbs: " + str(form.total_carbs.data))
        print("Total Protein: " + str(form.total_protein.data))
        print("Total Calories: " + str(form.total_calories.data))
        fcn_update_from_form(form,meal_id,'UpdateMeal')
        #TODO: Update Meal info here
        #TODO: Change create_meal to textfield
        flash('Meal has been updated', 'success')
        return redirect(url_for('update_meal',meal_id = meal.id))
    elif request.method == 'GET':

        form.name.data = meal.name
        form.recipe.data = meal.recipe
        form.notes.data = meal.notes
        form.favorite.data = meal.favorite
        form.date_eaten.data = meal.date_eaten
        form.exclude_from_daily.data = meal.exclude_from_daily

        form.total_protein.data = meal.protein
        form.total_carbs.data = meal.carbs
        form.total_fat.data = meal.fat
        form.total_calories.data = meal.calories


        form.serv_weight.data = meal.serv_weight
        form.serv_volume.data = meal.serv_volume
        form.serv_count.data = meal.serv_count

        form.drop_weight.data = meal.weight_unit_id
        form.drop_volume.data = meal.volume_unit_id
        form.drop_count.data = meal.count_unit_id
        
        for i,mi in enumerate(meal.meal_ingredients):
            form['amount%d' % mi.id].data=mi.serv
            form['unit%d' % mi.id].data=mi.unit_id

    return render_template('create_meal.html',title='Meal',form=form, meal=meal, ingr_list=ingr_list, unit_dict = unit_dict)


@app.route("/meals/<int:meal_id>/add", methods=['GET','POST'])
@login_required
def add_ingredients_to_meal(meal_id):
    if request.method == 'POST':
        ingredient_id_list = parse_element(request.form,'check')
        add_ingredients(ingredient_id_list, meal_id)
        flash('Your ingredient have been added', 'success')
        return redirect(url_for('update_meal',meal_id=meal_id))
    ingredients = Ingredients.query.filter_by(user_id = current_user.id, obsolete = False).all()
    return render_template('ingredients.html',title='Ingredients', ingredients=ingredients)

@app.route("/meals/<int:meal_id>/add_meal_to_ingredients", methods=['GET','POST'])
@login_required
def add_meal_to_ingredients(meal_id):
    fcn_update_from_form(None, meal_id,'NewMealToIngredient')
    return redirect(url_for('ingredients'))


@app.route("/meals/<int:meal_id>/delete", methods=['POST'])
@login_required
def delete_meal(meal_id):
    meal = Meals.query.get_or_404(meal_id)
    if current_user != meal.author:
        abort(403)
    meal.obsolete = True
    db.session.commit()
    flash('Your meal has been deleted', 'success')
    return redirect(url_for('meals'))