import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from dietapp import app, db, bcrypt
from dietapp.forms import RegistrationForm, LoginForm, IngredientForm, MealForm
from dietapp.models import User, Ingredients, Units, UnitType, Meals, MealIngredients
from flask_login import login_user, current_user, logout_user, login_required
from collections import namedtuple


@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('home.html', title='Home')


def parse_checkboxes(form):
    ingredient_id_list = []
    for v in form:
        id = str(v).split("check")[1]
        #print (str(v) + ": " + str(form[v]) + " - " + id[1])
        if ("check" in v) and str(form[v]) == 'on':
            ingredient_id_list.append(id)
            print (str(v) + ": " + str(form[v]) + " - " + id)


    print(ingredient_id_list)
    return ingredient_id_list

@app.route('/ingredients', methods=['GET','POST'])
@login_required
def ingredients():
    if request.method == 'POST':
        #print("Check1: " + str(request.form.get("check1")))
        #print("Check2: " + str(request.form.get("check2")))
        ingredient_id_list = parse_checkboxes(request.form)
        delete_ingredients(ingredient_id_list)
    ingredients = Ingredients.query.filter_by(user_id = current_user.id, obsolete = False).all()
    return render_template('ingredients.html',title='Ingredients', ingredients=ingredients)

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



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def fcn_save_ingredient(form):
    ingredient = Ingredients(brand=form.brand.data, name=form.name.data, 
        fat=form.fat.data, carbs=form.carbs.data, protein=form.protein.data, calories=form.calories.data, 
        user_id=current_user.id)

    ingredient.serv_weight=form.serv_weight.data
    ingredient.weight_unit_id=form.drop_weight.data
    ingredient.serv_volume=form.serv_volume.data
    ingredient.volume_unit_id=form.drop_volume.data
    ingredient.serv_count=form.serv_count.data
    ingredient.count_unit_id=form.drop_count.data
    
    
    db.session.add(ingredient)
    db.session.commit()

def fcn_update_ingredient(form, ingredient_id):
    ingredient = Ingredients.query.get(ingredient_id)

    ingredient.brand=form.brand.data
    ingredient.name=form.name.data
    ingredient.fat=form.fat.data
    ingredient.carbs=form.carbs.data
    ingredient.protein=form.protein.data
    ingredient.calories=form.calories.data 

    ingredient.serv_weight=form.serv_weight.data
    ingredient.weight_unit_id=form.drop_weight.data
    ingredient.serv_volume=form.serv_volume.data
    ingredient.volume_unit_id=form.drop_volume.data
    ingredient.serv_count=form.serv_count.data
    ingredient.count_unit_id=form.drop_count.data

    db.session.commit()

@app.route("/ingredients/new", methods=['GET','POST'])
@login_required
def new_ingredient():
    form = IngredientForm()
    
    form.drop_weight.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=1).all()]
    form.drop_volume.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=2).all()]
    form.drop_count.choices = [(g.id, g.name) for g in Units.query.filter_by(unit_type_id=3).all()]

    if form.validate_on_submit():
        fcn_save_ingredient(form)
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
        fcn_update_ingredient(form, ingredient_id)
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

    return render_template('create_ingredient.html',title='Update Post',form=form, legend='Update Post')



@app.route("/meals")
@login_required
def meals():
    meals = Meals.query.filter_by(user_id = current_user.id, obsolete = False).all()
    return render_template('meals.html',title='Meal', meals=meals)


def create_ingr_list(meal):
    ingr_list = []
    for i,mi in enumerate(meal.meal_ingredients):
        serving_unit = Units.query.filter_by(id=mi.unit_id).first()

        if(serving_unit.unit_type_id == 1):
            ingr_unit = Units.query.filter_by(id=mi.ingredient.weight_unit_id).first()
            ingr_serving_amount = mi.ingredient.serv_weight
        elif(serving_unit.unit_type_id == 2):
            ingr_unit = Units.query.filter_by(id=mi.ingredient.volume_unit_id).first()
            ingr_serving_amount = mi.ingredient.serv_volume
        else:
            ingr_unit = Units.query.filter_by(id=mi.ingredient.count_unit_id).first()
            ingr_serving_amount = mi.ingredient.serv_count


        d = {}
        d['IngrID'] = mi.ingredient.id
        d['IngrName'] = mi.ingredient.name
        d['IngrBrand'] = mi.ingredient.brand
        d['IngrFat'] = mi.ingredient.fat
        d['IngrCarbs'] = mi.ingredient.carbs
        d['IngrProtein'] = mi.ingredient.protein
        d['IngrCalories'] = mi.ingredient.calories
        d['IngrWeightAmount'] = mi.ingredient.serv_weight
        d['IngrVolumeAmount'] = mi.ingredient.serv_volume
        d['IngrCountAmount'] = mi.ingredient.serv_count
        d['IngrWeightUnitID'] = mi.ingredient.weight_unit_id
        d['IngrVolumeUnitID'] = mi.ingredient.volume_unit_id
        d['IngrCountUnitID'] = mi.ingredient.count_unit_id

        d['ServingUnit'] = serving_unit.name
        d['ServingAmount'] = mi.serv
        d['ServingFat'] = mi.ingredient.fat * mi.serv * serving_unit.conversion / (ingr_serving_amount * ingr_unit.conversion)
        d['ServingCarbs'] = mi.ingredient.carbs * mi.serv * serving_unit.conversion / (ingr_serving_amount * ingr_unit.conversion)
        d['ServingProtein'] = mi.ingredient.protein * mi.serv * serving_unit.conversion / (ingr_serving_amount * ingr_unit.conversion)
        d['ServingCalories'] = mi.ingredient.calories * mi.serv * serving_unit.conversion / (ingr_serving_amount * ingr_unit.conversion)

        ingr_list.append(d)

    return ingr_list

def create_unit_dict():
    units = Units.query.all()
    unit_dict = {}
    for i,u in enumerate(units):
        d = {}
        d["id"] = u.id
        d["Name"] = u.name
        d["Conversion"] = u.conversion
        d["UnitTypeID"] = u.unit_type_id

        unit_dict[u.id] = d

    return unit_dict


@app.route("/meals/<int:meal_id>/update", methods=['GET','POST'])
@login_required
def update_meal(meal_id):
    meal = Meals.query.get_or_404(meal_id)
    if current_user != meal.author:
        abort(403)

    form = MealForm(meal)
    if form.validate_on_submit():
        print("Total Name: " + str(form.name.data))
        print("Total Fat: " + str(request.form.get("total_fat")))
        print("Total Carbs: " + str(request.form.get("total_carbs")))
        print("Total Protein: " + str(request.form.get("total_protein")))
        print("Total Calories: " + str(request.form.get("total_calories")))
        #TODO: Update Meal info here
        #TODO: Change create_meal to textfield
        #print(form.TotalFat.data)
        flash('Meal has been updated', 'success')
        return redirect(url_for('update_meal',meal_id = meal.id))
    elif request.method == 'GET':
        ingr_list = create_ingr_list(meal)
        unit_dict = create_unit_dict()

    return render_template('create_meal.html',title='Meal',form=form, meal=meal, ingr_list=ingr_list, unit_dict = unit_dict)


@login_required
def delete_ingredients(ingredient_id_list):
    for id in ingredient_id_list:
        ingredient = Ingredients.query.get_or_404(id)
        if current_user != ingredient.author:
            abort(403)
        ingredient.obsolete = True
        db.session.commit()
    flash('Your ingredient has been deleted', 'success')
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

