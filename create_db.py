from dietapp import db, bcrypt
from dietapp.models import User, Ingredients, Units, UnitType, MealIngredients, Meals

db.drop_all()
db.create_all()

u1 = User(username="rdudaney", email="rohan.dudaney@gmail.com", password=bcrypt.generate_password_hash("test").decode('utf-8'))
u2 = User(username="test", email="test@test.com", password=bcrypt.generate_password_hash("test").decode('utf-8'))

db.session.add(u1)
db.session.add(u2)

weight = UnitType(typ="weight")
volume = UnitType(typ="Volume")
count = UnitType(typ="count")

db.session.add(weight)
db.session.add(volume)
db.session.add(count)


g1 = Units(name="g", obsolete=False,unit_type_id=1)
g2 = Units(name="oz", obsolete=False,unit_type_id=1)

g3 = Units(name="cup", obsolete=False,unit_type_id=2)
g4 = Units(name="mL", obsolete=False,unit_type_id=2)

g5 = Units(name="scoops", obsolete=False,unit_type_id=3)
g6 = Units(name="pieces", obsolete=False,unit_type_id=3)

db.session.add(g1)
db.session.add(g2)
db.session.add(g3)
db.session.add(g4)
db.session.add(g5)
db.session.add(g6)


i1 = Ingredients(brand='Lactaid', name='Skim Milk', protein=8, carbs=13, fat=0, calories=84, serv_weight=236.588, weight_unit_id=1, serv_volume=1, volume_unit_id=3, user_id=1)
i2 = Ingredients(brand='Integrated Supplements', name='Protein Powder', protein=20, carbs=6, fat=1.5, calories=84, serv_weight=31, weight_unit_id=1, serv_count=2, count_unit_id=5, user_id=1)

db.session.add(i1)
db.session.add(i2)


m1 = Meals(name='Test Meal',protein=1, carbs=2, fat=3, calories=4, serv_weight=20,weight_unit_id=1, user_id=1)
db.session.add(m1)

mi1 = MealIngredients(meal_id=1,ingredient_id=1, unit_id=3, serv=1.5)
mi2 = MealIngredients(meal_id=1,ingredient_id=2, unit_id=5, serv=2)
db.session.add(mi1)
db.session.add(mi2)


db.session.commit()