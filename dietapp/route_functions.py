from dietapp import app, db, bcrypt
from dietapp.models import User, Ingredients, Units, UnitType, Meals, MealIngredients
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, abort, jsonify

def parse_checkboxes(form):
    #TODO: Make generic so it just finds the number
    ingredient_id_list = []
    for v in form:
        id = str(v).split("check")[1]
        if ("check" in v) and str(form[v]) == 'on':
            ingredient_id_list.append(id)

    return ingredient_id_list


def fcn_save_new_from_form(form, save_type):
    if save_type == 'NewIngredient':
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

def fcn_update_from_form(form, id, update_type):
    if update_type == 'UpdateIngredient':
        ingredient = Ingredients.query.get(id)

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

    if update_type == 'UpdateMeal':
        meal = Meals.query.get(id)

        meal.name = form.name.data

        meal.recipe = form.recipe.data
        meal.notes = form.notes.data
        meal.favorite = form.favorite.data

        meal.serv_weight = form.serv_weight.data
        meal.serv_volume = form.serv_volume.data
        meal.serv_count = form.serv_count.data

        meal.weight_unit_id = form.drop_weight.data
        meal.volume_unit_id = form.drop_volume.data
        meal.count_unit_id = form.drop_count.data

    db.session.commit()


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
        d["MealIngrID"] = mi.id
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


@login_required
def add_ingredients(ingredient_id_list, meal_id):
    meal = Meals.query.get_or_404(meal_id)
    if current_user != meal.author:
        abort(403)
    for id in ingredient_id_list:
        ingredient = Ingredients.query.get_or_404(id)
        if current_user != ingredient.author:
            abort(403)
        #TODO: Fix ingredient serving id error
        if ingredient.weight_unit_id is not None:
            mi_unit_id = ingredient.weight_unit_id
        elif ingredient.volume_unit_id is not None:
            mi_unit_id = ingredient.volume_unit_id
        elif ingredient.count_unit_id is not None:
            mi_unit_id = ingredient.count_unit_id
        mi = MealIngredients(meal_id=meal_id,ingredient_id=id,serv=0,unit_id=mi_unit_id)
        db.session.add(mi)
    db.session.commit()
    #TODO: Remove  return redirect
    return redirect(url_for('update_meal',meal_id=meal_id))

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

