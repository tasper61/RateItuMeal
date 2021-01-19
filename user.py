from flask import current_app, flash
from flask_login import UserMixin
import database as db
import current_meal
from datetime import datetime, timedelta 


class User(UserMixin):
    def __init__(self, user_id, username, password, type_ = "Student"):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.username
    
    @property
    def is_active(self):
        return self.active
    
    def is_authenticated(self):
        return True
    
    def give_vote(self,taste, appearence, freshness, name_):
        db = current_app.config["db"]
        user_id = self.user_id
        food_id = db.get_food(name_)
        if db.give_vote(taste, appearence, freshness, user_id,food_id):
            return True 
        else:
            print("Oy verilemedi")
            return None    

    def give_comment(self,text, meal_id=0):
        db = current_app.config["db"]
        current_m = current_app.config["current_m"]
        user_id = self.user_id
        if(meal_id == 0):
            meal_id = current_m.id
        if not db.give_comment(text, meal_id, user_id,self.is_admin):
            flash("Please enter shorter comment")

    def get_user_comments(self):
        db = current_app.config["db"]
        user_id = self.user_id
        return db.get_user_comments(user_id, self.is_admin)
    
    def get_user_vote_counter(self):
        db = current_app.config["db"]
        user_id = self.user_id
        return db.get_user_vote_counter(user_id)
    
    def get_user_average_rate(self):
        db = current_app.config["db"]
        user_id = self.user_id
        return db.get_user_average_rate(user_id)
    
    def rate_meal(self,overall, meal_id):
        db = current_app.config["db"]
        db.rate_meal(overall, meal_id,self.user_id)
        return True

def get_user(username, type_="Student"):
    db = current_app.config["db"]
    user_id, username, password, typ= db.get_user(username, type_)
    user = User(user_id, username, password, typ) if password else None
    if user is not None:
        user.is_admin = db.is_chief(user.username)
    return user


def create_user(username, password, type_):
    db = current_app.config["db"]
    if db.create_user(username, password, type_):
        user_id = db.get_user(username, type_)
        user = User(user_id, username, password)
        return user
    else:
        return None

def insert_food(category, calorie, name_):
    db = current_app.config["db"]
    if db.insert_food(category, calorie, name_):
        print(category, calorie, name_)
        return True
    else:
        return None

def get_comments(meal_id):
    if(meal_id is not None):
        db = current_app.config["db"]
        comments = db.get_comments(meal_id)
        return comments
    else:
        return None
def get_best_foods():
    db = current_app.config["db"]
    best_foods = db.get_best_foods()
    return best_foods

def get_between_meals(begin, end,sort):
    db = current_app.config["db"]
    meals = db.get_between_meals(begin, end, sort)
    return meals
def get_weekly_proposed_meals():
    db = current_app.config["db"]
    today = datetime.date(datetime.today())
    end = today-timedelta(days = 7)
    meal_student_ids = db.get_between_meals(str(end), str(today), "average", 0)
    list = [[0 for x in range(2)] for y in range(len(meal_student_ids))]
    db = current_app.config["db"]
    for i in range(len(meal_student_ids)):
        current_m = current_meal.Current_Meal()
        current_m.meal(meal_student_ids[i][0])
        current_m.get_average_rates()
        current_m.get_vote_counter()
        current_m.get_food_calories()
        current_m.id = meal_student_ids[i][0]
        current_m.get_score()
        list[i][0] = current_m
        list[i][1] = db.get_username(meal_student_ids[i][1])

    return list
