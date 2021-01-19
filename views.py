from flask import current_app, render_template, request, redirect, url_for, flash,session,jsonify
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
import forms
import user as usr
import current_meal
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from functools import wraps
from flask import abort

@login_required
def home_page():
    if request.method == "GET":
        today = datetime.today()
        db = current_app.config["db"]
        count = db.get_meal_count(today.date())
        scrape = False
        if( (today.hour > 14) and (count < 2)):
           scrape = True
        if( (today.hour > 8) and (count < 1)):
           scrape = True
        if scrape :
            current_m = current_meal.Current_Meal()
            current_m.Itu_meal()
            current_app.config["current_m"] = current_m
        else:
            current_m = current_meal.Current_Meal()
            current_m.id = db.find_meal_with_date(today.date())
            current_m.meal(current_m.id)
            current_m.get_food_calories()
            current_app.config["current_m"] = current_m
        current_m = current_app.config["current_m"]
        current_m.get_vote_counter()
        current_m.get_average_rates()
        current_m.get_score()
        comments, chief_comments= usr.get_comments(current_m.id)
        return render_template("home2.html",current_m = current_m, comments = comments,is_chief = current_user.is_admin,chief_comments = chief_comments)
    else:
        current_m = current_app.config["current_m"]
        taste = request.form.get('Taste')
        appearance = request.form.get('Appearance')
        freshness = request.form.get('Freshness')
        overall = request.form.get('Overall')
        comment = request.form["Comment_"]
        food_name = None
        #user = usr.get_user(current_user.get_id())
        if request.form.get('foods') == "Corba" :
            food_name = current_m.food_names[0]
            current_user.give_vote(taste,appearance,freshness,food_name)
        elif request.form.get('foods') == "Main Course" :
            food_name = current_m.food_names[1]
            current_user.give_vote(taste,appearance,freshness,food_name)
        elif request.form.get('foods') == "Ara Yemek" :
            food_name = current_m.food_names[2]
            current_user.give_vote(taste,appearance,freshness,food_name)
        elif request.form.get('foods') == "Tatli" :
            food_name = current_m.food_names[3]
            current_user.give_vote(taste,appearance,freshness,food_name)
        overall = request.form.get('Overall')
        if (overall != '0' and overall != None):
            current_user.rate_meal(overall, current_m.id)
        if (comment != ''):
            current_user.give_comment(comment)
        current_m.get_vote_counter()
        current_m.get_average_rates()
        current_m.get_score()
        comments,chief_comments = usr.get_comments(current_m.id)
        return render_template("home2.html",current_m = current_m, comments = comments,is_chief = current_user.is_admin, chief_comments = chief_comments)

def meal_page(meal_id):
    if request.method == "GET":    
        current_m = current_meal.Current_Meal()
        current_m.meal(meal_id)
        if(current_m.food_names is None):
            abort(404)
        current_m.get_average_rates()
        current_m.get_vote_counter()
        current_m.get_food_calories()
        current_m.id = meal_id
        current_m.get_score()
        comments,chief_comments = usr.get_comments(current_m.id)
        return render_template("meal.html",current_m = current_m,chief_comments = chief_comments,comments = comments)
    else:
        comment = request.form["Comment_"]
        if (comment != ''):
            current_user.give_comment(comment, meal_id)
        current_m = current_meal.Current_Meal()
        current_m.meal(meal_id)
        current_m.get_average_rates()
        current_m.get_vote_counter()
        current_m.get_food_calories()
        current_m.id = meal_id
        comments,chief_comments = usr.get_comments(current_m.id)
        return render_template("meal.html",current_m = current_m,chief_comments = chief_comments,comments = comments)

@login_required
def profile_page():
    print("profile page")
    if request.method == "GET":
        my_comments = current_user.get_user_comments()
        my_votes = current_user.get_user_vote_counter()
        average_rate = current_user.get_user_average_rate()
        best_foods = usr.get_best_foods()
        return render_template("profile.html", username = current_user.get_id(),my_comments = my_comments, 
        my_votes = my_votes, average_rate = average_rate, best_foods = best_foods)
    else:
        db = current_app.config["db"]
        soup = request.form.get('Soup')
        main = request.form.get('Main Course')
        ara = request.form.get('Yan Yemek')
        desert = request.form.get('Tatli')
        if (soup is not None):
            meal = current_meal.Current_Meal(soup, main, ara, desert)
            do = True
            for i in range(len(meal.food_ids)):
                if(meal.food_ids[i] == None):
                    do = False
                    flash("One or more foods that you suggested doesnt exist in database")
            if(do):
                a = db.create_meal(meal, current_user.user_id)
                if a is False:
                    flash("This meal already exist")
        begin = request.form.get('begin')
        end = request.form.get('end')
        sort = request.form.get('sorts')
        form_comment_keys = request.form.getlist("comment_id")
        for comment_id in form_comment_keys:
            db.delete_comment(comment_id)
        meals = None
        if begin is not None:
            meals=usr.get_between_meals(begin,end,sort)
        my_comments = current_user.get_user_comments()
        my_votes = current_user.get_user_vote_counter()
        average_rate = current_user.get_user_average_rate()
        best_foods = usr.get_best_foods()
        return render_template("profile.html", username = current_user.get_id(),my_comments = my_comments, 
        my_votes = my_votes, average_rate = average_rate, best_foods = best_foods, meals = meals)

def login_page():
    print("login page")
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = request.form["username"]
        user = usr.get_user(username)
        if user is not None:
            password = request.form["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                today = datetime.today()
                db = current_app.config["db"]
                count = db.get_meal_count(today.date())
                scrape = False
                if( (today.hour > 14) and (count < 2)):
                    scrape = True
                if( (today.hour >= 0) and (count < 1)):
                    scrape = True
                if scrape :
                    current_m = current_meal.Current_Meal()
                    current_m.Itu_meal()
                    current_app.config["current_m"] = current_m
                else:
                    current_m = current_meal.Current_Meal()
                    current_m.id = db.find_meal_with_date(today.date())
                    current_m.meal(current_m.id)
                    current_m.get_food_calories()
                    current_app.config["current_m"] = current_m
                current_m = current_app.config["current_m"]
                comments, chief_comments= usr.get_comments(current_m.id)
                next_page = request.args.get("next", url_for("home_page",current_m = current_m,comments = comments,is_chief = current_user.is_admin, chief_comments = chief_comments))
                return redirect(next_page)
        flash("Wrong username or password")
    return render_template("login2.html",form = form)

@login_required
def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("login_page"))

def create_user_page():
        form = forms.LoginForm()
        if form.validate_on_submit():
            username = request.form["username"]
            password = request.form["password"]
            type_ = request.form["type"]
            hashed = hasher.hash(password)
            new_user = usr.create_user(username, hashed, type_)
            if new_user is None:
                flash("Username exists")
            else:
                login_user(new_user)
                current_m = current_app.config["current_m"]
                next_page = request.args.get("next", url_for("home_page",current_m = current_m))
                return redirect(next_page)

        return render_template("create_user2.html", form=form)

def give_suggestions():
    input = request.form["data"]
    category = request.form["category"]
    print(input)
    if len(input) == 0:
        return {"data": []}
    else:
        db = current_app.config["db"]
        suggestions = db.get_suggestions(input,category)
        return {"data" : suggestions}

def proposals_page():
    print("Proposals Page")
    if request.method == "GET":
        list = usr.get_weekly_proposed_meals()
        return render_template("proposals.html",list = list)
    else:
        overall = request.form.get('Overall')
        meal_id = request.form.get('rdio')
        if(current_user.is_admin):
            flash("Chiefs cannot vote meals")
        else:
            if (overall != '0'):
                current_user.rate_meal(overall, meal_id)
        list = usr.get_weekly_proposed_meals()
        return render_template("proposals.html",list = list)
