#https://stackoverflow.com/questions/17972020/how-to-execute-raw-sql-in-flask-sqlalchemy-app
from dietapp import db, bcrypt
from dietapp.models import User, Ingredients, Units, UnitType, MealIngredients, Meals
from sqlalchemy import text

# result = db.engine.execute("SELECT date_created FROM Meals")
# db.engine.execute("ALTER TABLE Meals ADD COLUMN temp Text")
# db.engine.execute("UPDATE Meals Set temp = date(date_created)")
# db.engine.execute("ALTER TABLE Meals RENAME COLUMN temp To date_eaten")

# result = db.engine.execute("SELECT date_eaten, calories FROM Meals")
# result = db.engine.execute("SELECT date_eaten, SUM(calories) as daily_calories, SUM(carbs) as daily_carbs, SUM(protein) as daily_protein, SUM(fat) as daily_fat FROM Meals GROUP BY date_eaten ORDER BY date_eaten DESC")

# print(result)
# for row in result:
#     for i in row:
#         print("%5s" % (i), end="    ")
#     print()

# db.engine.execute("ALTER TABLE Meals ADD COLUMN exclude_from_daily Boolean")
db.engine.execute("UPDATE Ingredients Set obsolete = False WHERE id = 49 ")
# result = db.engine.execute("PRAGMA table_info(Meals)")

# print(result)
# for row in result:
#     for i in row:
#         print("%5s" % (i), end="    ")
#     print()

