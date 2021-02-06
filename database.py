import MySQLdb as dbapi2
import current_meal
from datetime import datetime, timedelta
from flask import flash

class Database:
    def __init__(self, host="", user="", passwd="", db=""):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    def create_user(self, username, password, type_):
        # password will be passed as hashed to this function
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT student_id FROM students ORDER BY student_id DESC LIMIT 1"""
            cursor.execute(statement)
            fetch = cursor.fetchall()
            if len(fetch) == 0:
                student_id = 1
            else:
                student_id = fetch[0][0]+1
            statement = """SELECT chief_id FROM chiefs ORDER BY chief_id DESC LIMIT 1"""
            cursor.execute(statement)
            fetch = cursor.fetchall()
            if len(fetch) == 0:
                chief_id = 1
            else:
                chief_id = fetch[0][0]+1
            if(student_id > chief_id):
                id = student_id
            else:
                id = chief_id
            try:
                # creating a user tuple
                if(type_ == "Student"):
                    statement = """SELECT * FROM chiefs WHERE username = %s"""
                    cursor.execute(statement, (username, ))
                    fetch = cursor.fetchall()
                    if(len(fetch) == 0):
                        statement = """INSERT INTO students(student_id,username, password_) VALUES(%s,%s, %s)"""
                        cursor.execute(statement,(id,username, password))
                        connection.commit()
                        cursor.close()
                    else:
                        print("Bu kullanıcı mevcut")
                        return False
                elif(type_ == "Chief"):
                    statement = """SELECT * FROM students WHERE username = %s"""
                    cursor.execute(statement, (username, ))
                    fetch = cursor.fetchall()
                    if(len(fetch) == 0):
                        
                        statement = """INSERT INTO chiefs(chief_id,username, password_) VALUES(%s,%s, %s)"""
                        cursor.execute(statement,(id,username, password))
                        connection.commit()
                        cursor.close()
                    else:
                        print("Bu kullanıcı mevcut")
                        return False

            except dbapi2.IntegrityError:
                #print("username exists")
                connection.rollback()
                return False

        return True

    def get_user(self, username, type_= "Student"):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:

            cursor = connection.cursor()
            statement = """SELECT * FROM students WHERE username = %s"""
            cursor.execute(statement, (username, ))
            fetch = cursor.fetchall()
            if len(fetch) == 0:
                statement = """SELECT * FROM chiefs WHERE username = %s"""
                cursor.execute(statement, (username, ))
                fetch = cursor.fetchall()
                if len(fetch) == 0:
                    return None, None, None, None
                else:    
                    user_id= fetch[0][0]
                    username = fetch[0][1]
                    password = fetch[0][2]
                    cursor.close()
                    return user_id, username, password, "Chief" 
                cursor.close()
                return None, None, None, None
            
            user_id= fetch[0][0]
            username = fetch[0][1]
            password = fetch[0][2]
            cursor.close()
            return user_id, username, password, type_
    
    def is_chief(self, username):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM chiefs WHERE username = %s"""
            cursor.execute(statement, (username, ))
            fetch = cursor.fetchall()
            if(len(fetch) == 0):
                return False
            return True

    def insert_food(self, category, calorie, name_):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            calorie = calorie.replace(',','.')
            calorie = float(calorie)
            try:
                statement = """INSERT INTO foods(category, calorie, name_) VALUES(%s, %s, %s)"""
                cursor.execute(statement, (category, calorie, name_))
                connection.commit()
                cursor.close()
            except dbapi2.IntegrityError:
                connection.rollback()
                return False
        return True
    def get_food(self, name_):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT food_id FROM foods WHERE name_ = %s"""
            #print(name_)
            food_name = name_
            cursor.execute(statement, (food_name,))
            fetch = cursor.fetchall()
            if(len(fetch) == 0):
                cursor.close()
                #print("OYLE BİR FOOD YOK")
                return None
            food_id = fetch[0][0]
            cursor.close()
            return food_id

    def give_vote(self, taste, appearence, freshness,student_id,food_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
        
            try:
                statement = """INSERT INTO votes(taste, appearence, freshness, student_id, food_id) VALUES(%s, %s, %s, %s, %s)"""
                cursor.execute(statement,(taste, appearence, freshness, student_id, food_id))
                connection.commit()
                cursor.close()
            except dbapi2.IntegrityError:
                connection.rollback()
                return False
        return True

    def get_vote_counter(self,food_name):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            food_id = self.get_food(food_name)
            statement = """SELECT COUNT(*) FROM votes WHERE food_id = %s"""
            cursor.execute(statement,(food_id,))
            fetch = cursor.fetchall()
            vote_count = fetch[0][0]
            cursor.close()
            return vote_count
    
    def get_food_calorie(self, food_name):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = "SELECT calorie from foods WHERE name_ = %s"
            cursor.execute(statement, (food_name,))
            fetch = cursor.fetchall()
            cursor.close()
            if(len(fetch) != 0):
                return fetch[0][0]
            else:
                print("Food un kalorisi bulunamadı")
                return 0


    def get_meal_score(self, meal_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT AVG(overall) FROM meal_votes WHERE meal_id = %s """
            cursor.execute(statement, (meal_id, ))
            fetch = cursor.fetchall()
            cursor.close()
            if fetch[0][0] is None:
                return 0
            else:
                return round(fetch[0][0],2)

    def get_meal_vote_count(self, meal_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT COUNT(*) FROM meal_votes WHERE meal_id = %s """
            cursor.execute(statement, (meal_id, ))
            fetch = cursor.fetchall()
            cursor.close()
            return fetch[0][0]
    
    def get_average_rate(self, food_name):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            food_id = self.get_food(food_name)
            statement = """SELECT SUM(taste + appearence + freshness) from votes WHERE food_id = %s"""
            cursor.execute(statement,(food_id,))
            fetch = cursor.fetchall()
            sum_rate = fetch[0][0]
            if(sum_rate is None):
                sum_rate = 0
            cursor.close()
            try:
                average_rate = sum_rate / (self.get_vote_counter(food_name) *3)
            except:
                average_rate = 0
            average_rate = round(average_rate, 2)
            return average_rate
    
    def create_meal(self,new_meal, student_id=1):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            today = datetime.today()
            cursor = connection.cursor()
            if(self.is_meal_exist(new_meal.food_ids, student_id)):
                try:
                    statement = """INSERT INTO meals(score, date_, student_id) VALUES(%s, %s, %s)"""
                    print(today.date(), student_id)
                    cursor.execute(statement,(0, today.date(), student_id,))
                    connection.commit()
                    cursor.close()
                except dbapi2.IntegrityError:
                    print("yyyy")
                    connection.rollback()
                    return False
                created = self.add_foods_to_meal(new_meal.food_ids)
                return created
            return False
    
    def add_foods_to_meal(self, food_ids):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            meal_id = self.get_lastrow_meal_id()
            try:
                statement = """INSERT INTO prepares(meal_id, food_id) VALUES(%s, %s)"""
                cursor.execute(statement,(meal_id,food_ids[0]))
                statement = """INSERT INTO prepares(meal_id, food_id) VALUES(%s, %s)"""
                cursor.execute(statement,(meal_id,food_ids[1]))
                statement = """INSERT INTO prepares(meal_id, food_id) VALUES(%s, %s)"""
                cursor.execute(statement,(meal_id,food_ids[2]))
                statement = """INSERT INTO prepares(meal_id, food_id) VALUES(%s, %s)"""
                cursor.execute(statement,(meal_id,food_ids[3]))
                connection.commit()
                cursor.close()
            except dbapi2.IntegrityError:
                connection.rollback()
                return False
        return True

    def get_lastrow_meal_id(self):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT meal_id FROM meals ORDER BY meal_id DESC LIMIT 1"""
            cursor.execute(statement)
            fetch = cursor.fetchall()
            meal_id = fetch[0][0]
            cursor.close()
            return meal_id

    def is_meal_exist(self, food_ids, student_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT student_id,prepares.meal_id, COUNT(*) FROM prepares INNER JOIN meals ON meals.meal_id = prepares.meal_id where food_id = %s OR food_id = %s OR food_id = %s OR food_id = %s group by meal_id"""
            cursor.execute(statement,(food_ids[0],food_ids[1],food_ids[2],food_ids[3],))
            fetch = cursor.fetchall()
            print(food_ids)
            print("   ", fetch)
            if(cursor.rowcount == 0):
                print("this meal does not exist")
                return True
            for i in range(len(fetch)):
                if(fetch[i][2] == 4):
                    if(((student_id == 1) and (fetch[i][0] != 1))):
                        print("This meal exist butttt another student suggested that so new one created for ıtu meal")
                    else:    
                        print("This meal already exist")
                        return False
            print("xxxx")
            cursor.close()            
            return True
    
    def get_meal_id(self, food_ids):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT meal_id,COUNT(*) FROM prepares where food_id = %s OR food_id = %s OR food_id = %s OR food_id = %s group by meal_id"""
            cursor.execute(statement,(food_ids[0],food_ids[1],food_ids[2],food_ids[3],))
            fetch = cursor.fetchall()
            #print(fetch[0][0])
            cursor.close()
            for i in range(len(fetch)):
                if(fetch[i][1] == 4):
                    return fetch[i][0]
            else:
                print("Get_meal_id() istenilenen meal i bulamadı")
            
    def find_meal_with_date(self, today):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = "SELECT meal_id FROM meals WHERE date_ = %s and student_id = 1"
            cursor.execute(statement,(today,))
            fetch = cursor.fetchall()
            cursor.close()
            if(len(fetch) == 2):
                return fetch[1][0]
            else:
                return fetch[0][0]


    def give_comment(self, text, meal_id , user_id, is_chief):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
        
            try:
                if(is_chief):
                    statement = """INSERT INTO comments(text_, meal_id, chief_id) VALUES(%s, %s, %s)"""
                else:
                    statement = """INSERT INTO comments(text_, meal_id, student_id) VALUES(%s, %s, %s)"""
                cursor.execute(statement,(text, meal_id, user_id))
                connection.commit()
                cursor.close()
            except :
                connection.rollback()
                return False
        return True
    def get_username(self, id):
         with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT username FROM students WHERE student_id = %s """
            cursor.execute(statement, (id,))
            fetch = cursor.fetchall()
            cursor.close()
            if(len(fetch) == 0):
                return None
            return fetch[0][0]
    def get_username_chief(self, id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT username FROM chiefs WHERE chief_id = %s """
            cursor.execute(statement, (id,))
            fetch = cursor.fetchall()
            cursor.close()
            if(len(fetch) == 0):
                return None
            return fetch[0][0]

    def get_comments(self, meal_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT text_, student_id FROM comments WHERE meal_id = %s AND student_id is not NULL """
            cursor.execute(statement, (meal_id,))
            fetch = cursor.fetchall()
            if(len(fetch) == 0):
                cursor.close()
                return None,None
            else:
                i = 0
                comments = [[0 for x in range(2)] for y in range(cursor.rowcount)]
                while(i < cursor.rowcount):
                    comments[i][0] = fetch[i][0]
                    comments[i][1] = self.get_username(fetch[i][1])
                    i+=1
                statement = """SELECT text_, chief_id FROM comments WHERE meal_id = %s AND chief_id is not NULL"""
                cursor.execute(statement, (meal_id,))
                fetch = cursor.fetchall()
                i = 0
                chief_comments = [[0 for x in range(2)] for y in range(cursor.rowcount)]
                while(i < cursor.rowcount):
                    chief_comments[i][0] = fetch[i][0]
                    chief_comments[i][1] = self.get_username_chief(fetch[i][1])
                    i+=1
                cursor.close()
            return comments, chief_comments

    def get_user_comments(self, user_id, is_chief):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            if(is_chief):
                statement = """SELECT comment_id, text_, meal_id FROM comments WHERE chief_id = %s"""
            else:
                statement = """SELECT comment_id, text_, meal_id FROM comments WHERE student_id = %s"""
            cursor.execute(statement,(user_id,))
            fetch = cursor.fetchall()
            my_comments=[[0 for x in range(3)] for y in range(cursor.rowcount)]
            i = 0
            while(i < cursor.rowcount):
                my_comments[i][0] = fetch[i][0]
                my_comments[i][1] = fetch[i][1]
                my_comments[i][2] = fetch[i][2]
                i+=1
            cursor.close()
            return my_comments

    def get_user_vote_counter(self,user_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT COUNT(*) FROM votes WHERE student_id = %s"""
            cursor.execute(statement,(user_id,))
            fetch = cursor.fetchall()
            vote_count = fetch[0][0]
            cursor.close()
            return vote_count 

    def get_user_average_rate(self, user_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT SUM(taste + appearence + freshness) from votes WHERE student_id = %s"""
            cursor.execute(statement,(user_id,))
            fetch = cursor.fetchall()
            sum_rate = fetch[0][0]
            if(sum_rate is None):
                sum_rate = 0
            cursor.close()
            try:
                average_rate = sum_rate / (self.get_user_vote_counter(user_id) *3)
            except:
                average_rate = 0
            average_rate = round(average_rate, 2)
            return average_rate
    
    def get_best_foods(self):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            food_names = [[0 for x in range(2)] for y in range(4)]
            cursor = connection.cursor()
            statement = """SELECT name_,category,AVG(taste+freshness+appearence) as avg_rate from votes INNER JOIN foods ON votes.food_id = foods.food_id GROUP BY name_ HAVING category = "Soup" ORDER BY avg_rate DESC """
            cursor.execute(statement)
            fetch = cursor.fetchall()
            food_names[0][0] = fetch[0][0]
            food_names[0][1] = round(fetch[0][2]/3,2)
            statement = """SELECT name_,category,AVG(taste+freshness+appearence) as avg_rate from votes INNER JOIN foods ON votes.food_id = foods.food_id GROUP BY name_ HAVING category = "Main Course" ORDER BY avg_rate DESC """
            cursor.execute(statement)
            fetch = cursor.fetchall()
            food_names[1][0] = fetch[0][0]
            food_names[1][1] = round(fetch[0][2]/3,2)
            statement = """SELECT name_,category,AVG(taste+freshness+appearence) as avg_rate from votes INNER JOIN foods ON votes.food_id = foods.food_id GROUP BY name_ HAVING category = "Yan Yemek" ORDER BY avg_rate DESC """
            cursor.execute(statement)
            fetch = cursor.fetchall()
            food_names[2][0] = fetch[0][0]
            food_names[2][1] = round(fetch[0][2]/3,2)
            statement = """SELECT name_,category,AVG(taste+freshness+appearence) as avg_rate from votes INNER JOIN foods ON votes.food_id = foods.food_id GROUP BY name_ HAVING category = "Tatli" ORDER BY avg_rate DESC """
            cursor.execute(statement)
            fetch = cursor.fetchall()
            food_names[3][0] = fetch[0][0]
            food_names[3][1] = round(fetch[0][2]/3,2)
            cursor.close()
            return food_names
    
    def get_meal(self, meal_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            food_names = []
            cursor = connection.cursor()
            statement = """SELECT name_ from prepares INNER JOIN foods ON prepares.food_id = foods.food_id WHERE meal_id = %s"""
            cursor.execute(statement,(meal_id,))
            fetch = cursor.fetchall()
            if(len(fetch) == 0):
                return None
            food_names.append(fetch[0][0])
            food_names.append(fetch[1][0])
            food_names.append(fetch[2][0])
            food_names.append(fetch[3][0])
            cursor.close()
            return food_names
    
    def get_between_meals(self,begin,end,sort,student_id = 1):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            meals = []
            cursor = connection.cursor()
            if(student_id == 0):
                statement = "SELECT meal_id,student_id from meals WHERE date_ >= '" + begin + "' AND date_ <= '" + end + "' AND student_id != 1 ORDER by " + sort + " DESC"
            else:
                statement = "SELECT meal_id,student_id from meals WHERE date_ >= '" + begin + "' AND date_ <= '" + end + "' AND student_id = "+ str(student_id) +" ORDER by " + sort + " DESC"
            cursor.execute(statement)
            fetch = cursor.fetchall()
            if(student_id == 0):
                meals_students = [[0 for x in range(2)] for y in range(cursor.rowcount)]
                i = 0
                while(i < cursor.rowcount):
                    meals_students[i][0] = fetch[i][0]
                    meals_students[i][1] = fetch[i][1]
                    i+=1
                cursor.close()
                return meals_students
            else:
                i = 0
                while(i < cursor.rowcount):
                    meals.append(fetch[i][0])
                    i+=1
                cursor.close()
                return meals
    
    def get_suggestions(self, text,category):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            suggestions = []
            cursor = connection.cursor()
            statement = """ SELECT name_ FROM foods where name_ like '""" + text + """%' and category= '"""+ category + """'"""
            cursor.execute(statement)
            fetch = cursor.fetchall()
            for i in range(len(fetch)):
                suggestions.append(fetch[i][0])
            cursor.close()

            return suggestions

    def rate_meal(self, overall, meal_id, student_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            try:
                statement = """INSERT INTO meal_votes(overall,meal_id,student_id) VALUES(%s,%s,%s)"""
                cursor.execute(statement,(overall, meal_id, student_id))
                connection.commit()
                cursor.close()
            except dbapi2.IntegrityError:
                flash(" You have already rated this meal")
                connection.rollback()
                return False
            self.set_meal_table(meal_id)            
        return True

    def set_meal_table(self, meal_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                vote_count = self.get_meal_vote_count(meal_id)
                statement = """UPDATE meals SET rate_counter = %s WHERE meal_id = %s"""
                cursor.execute(statement,(vote_count,meal_id))
                vote_average = self.get_meal_score(meal_id)
                statement = """UPDATE meals SET average = %s WHERE meal_id = %s"""
                cursor.execute(statement,(vote_average,meal_id))
                connection.commit()
                cursor.close()
            except:
                connection.rollback()
                print("Oylar meal tablosuna işlenemedi")
                return False
            return True
    
    
    def delete_comment(self, comment_id):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            try:
                statement = """DELETE FROM comments WHERE comment_id = %s"""
                cursor.execute(statement,([comment_id]))
                connection.commit()
                cursor.close()
            except dbapi2.IntegrityError:
                connection.rollback()
                return False
        return True

    def get_meal_count(self, today):
        with dbapi2.connect(charset='utf8',host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = "SELECT count(*) from meals WHERE date_ = %s and student_id = 1"
            cursor.execute(statement,(today,))
            fetch = cursor.fetchall()
            cursor.close()
            return fetch[0][0]


