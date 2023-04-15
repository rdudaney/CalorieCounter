from dietapp.ingredient import IngredientClass
from dietapp.models import Ingredients, Meals, MealIngredients
from dietapp import app, db, bcrypt


class MealClass:
    def __init__(self):
        self.id = 0
        self.user_id = 0

        self.name = ''
        self.recipe =''
        self.notes = ''
        self.favorite = False

        self.fat = 1
        self.carbs = 2
        self.protein = 3
        self.calories = 29

        self.serv_weight = 0.00
        self.serv_volume = 0.00
        self.serv_count = 0.00

        self.drop_weight = 0
        self.drop_volume = 0
        self.drop_count = 0

        self.ingredient_list = []
