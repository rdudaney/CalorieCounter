import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from dietapp import app, db, bcrypt
from dietapp.forms import RegistrationForm, LoginForm, IngredientForm, MealForm, create_MealForm
from dietapp.models import User, Ingredients, Units, UnitType, Meals, MealIngredients
from dietapp.route_functions import parse_element, fcn_save_new_from_form, fcn_update_from_form, create_ingr_list, \
    create_unit_dict, add_ingredients, delete_ingredients
from flask_login import login_user, current_user, logout_user, login_required
from collections import namedtuple


@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('home.html', title='Home')


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username = form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
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
        fcn_save_new_from_form(form, 'NewIngredient')
        flash('Your ingredient has been added!', 'success')
        return redirect(url_for('ingredients'))
    return render_template('create_ingredient.html',title='New Ingredient', legend='Add Ingredient', form = form)


@app.route("/ingredients/<int:ingredient_id>/update", methods=['GET','POST'])
@login_required
def update_ingredient(ingredient_id):
    ingredient = Ingredients.query.get_or_404(ingredient_id)
    if current_user != ingredient.author:
        abort(403)

    form = IngredientForm()
    form.drop_weight.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=1).all()]
    form.drop_volume.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=2).all()]
    form.drop_count.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=3).all()]


    if form.validate_on_submit():
        fcn_update_from_form(form, ingredient_id,'UpdateIngredient')
        flash('Ingredient has been updated', 'success')
        return redirect(url_for('update_ingredient',ingredient_id = ingredient.id))
    elif request.method == 'GET':
        form.brand.data = ingredient.brand
        form.name.data = ingredient.name
        form.fat.data = ingredient.fat
        form.carbs.data = ingredient.carbs
        form.protein.data = ingredient.protein
        form.calories.data = ingredient.calories
        form.serv_weight.data = ingredient.serv_weight
        form.serv_volume.data = ingredient.serv_volume
        form.serv_count.data = ingredient.serv_count


        form.drop_weight.data = ingredient.weight_unit_id
        form.drop_volume.data = ingredient.volume_unit_id
        form.drop_count.data = ingredient.count_unit_id

    return render_template('create_ingredient.html',title='Update Ingredient',form=form, legend='Update Ingredient')


@app.route("/meals")
@login_required
def meals():
    meals = Meals.query.filter_by(user_id = current_user.id, obsolete = False).all()
    return render_template('meals.html',title='Meal', meals=meals)


@app.route("/meals/<int:meal_id>/update", methods=['GET','POST'])
@login_required
def update_meal(meal_id):
    meal = Meals.query.get_or_404(meal_id)
    if current_user != meal.author:
        abort(403)

    create_MealForm(meal)
    form = MealForm()
    
    form.drop_weight.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=1).all()]
    form.drop_volume.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=2).all()]
    form.drop_count.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=3).all()]

    if form.validate_on_submit():
        print("Total Name: " + str(form.name.data))
        print("Total Fat: " + str(request.form.get("total_fat")))
        print("Total Carbs: " + str(request.form.get("total_carbs")))
        print("Total Protein: " + str(request.form.get("total_protein")))
        print("Total Calories: " + str(request.form.get("total_calories")))
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

        form.serv_weight.data = meal.serv_weight
        form.serv_volume.data = meal.serv_volume
        form.serv_count.data = meal.serv_count

        form.drop_weight.data = meal.weight_unit_id
        form.drop_volume.data = meal.volume_unit_id
        form.drop_count.data = meal.count_unit_id
        
        for i,mi in enumerate(meal.meal_ingredients):
            form['amount%d' % mi.id].data=mi.serv
            form['unit%d' % mi.id].data=mi.unit_id

        
        ingr_list = create_ingr_list(meal)
        unit_dict = create_unit_dict()

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