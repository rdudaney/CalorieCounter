from dietapp.models import Ingredients
from dietapp.forms import RegistrationForm, LoginForm, IngredientForm, MealForm, create_MealForm
from flask_login import login_user, current_user
from dietapp import app, db, bcrypt

class IngredientClass:
    def __init__(self, info, type):
        if type == "model":
            self._create_from_model(info)
        elif type == "form":
            self._create_from_form(info)

    def _create_from_form(self, form: IngredientForm):
        self.user_id=current_user.id
        self.id = 0

        self.update_from_form(form)

    def _create_from_model(self, model: Ingredients):
        self.user_id=model.user_id
        self.id = model.id

        self.name=model.name
        self.brand=model.brand
        
        self.fat=model.fat
        self.carbs=model.carbs
        self.protein=model.protein
        self.calories=model.calories 

        self.serv_weight=model.serv_weight
        self.serv_volume=model.serv_volume
        self.serv_count=model.serv_count

        self.drop_weight=model.weight_unit_id
        self.drop_volume=model.volume_unit_id
        self.drop_count =model.count_unit_id

    def update_from_form(self, form:IngredientForm):
        self.name=form.name.data
        self.brand=form.brand.data
        
        self.fat=form.fat.data
        self.carbs=form.carbs.data
        self.protein=form.protein.data
        self.calories=form.calories.data 

        self.serv_weight=form.serv_weight.data
        self.serv_volume=form.serv_volume.data
        self.serv_count=form.serv_count.data

        self.drop_weight=form.drop_weight.data
        self.drop_volume=form.drop_volume.data
        self.drop_count =form.drop_count.data

    def add_to_form(self,form: IngredientForm):

        form.brand.data = self.brand
        form.name.data = self.name

        form.fat.data = self.fat
        form.carbs.data = self.carbs
        form.protein.data = self.protein
        form.calories.data = self.calories

        form.serv_weight.data = self.serv_weight
        form.serv_volume.data = self.serv_volume
        form.serv_count.data = self.serv_count


        form.drop_weight.data = self.drop_weight
        form.drop_volume.data = self.drop_volume
        form.drop_count.data = self.drop_count

        return form


    def save(self):
        ingredient = None

        if self.id == 0:
            ingredient = Ingredients(brand=self.brand, name=self.name, 
                fat=self.fat, carbs=self.carbs, protein=self.protein, calories=self.calories, 
                user_id=self.user_id)
        else:
            ingredient = Ingredients.query.get(self.id)

            ingredient.brand=self.brand
            ingredient.name=self.name
            ingredient.fat=self.fat
            ingredient.carbs=self.carbs
            ingredient.protein=self.protein
            ingredient.calories=self.calories 
            ingredient.user_id=self.user_id

        ingredient.serv_weight=self.serv_weight
        ingredient.weight_unit_id=self.drop_weight
        ingredient.serv_volume=self.serv_volume
        ingredient.volume_unit_id=self.drop_volume
        ingredient.serv_count=self.serv_count
        ingredient.count_unit_id=self.drop_count

        if self.id == 0:
            db.session.add(ingredient)
            db.session.flush()
            self.id = ingredient.id

        db.session.commit()


        
