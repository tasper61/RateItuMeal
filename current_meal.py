import user as usr
import requests
from bs4 import BeautifulSoup
from flask import current_app
class Current_Meal:
    def __init__(self,s_name="", m_name="", a_name="", d_name=""):
        self.vote_counters = 0
        if(s_name != ""):
            self.food_names = []
            self.food_names.append(s_name.upper())
            self.food_names.append(m_name.upper())
            self.food_names.append(a_name.upper())
            self.food_names.append(d_name.upper())
            db = current_app.config["db"]
            self.food_ids = []
            self.food_ids.append(db.get_food(self.food_names[0]))
            self.food_ids.append(db.get_food(self.food_names[1]))
            self.food_ids.append(db.get_food(self.food_names[2]))
            self.food_ids.append(db.get_food(self.food_names[3])) 
        

    def get_vote_counter(self):
        if(self.food_names is not None):
            db = current_app.config["db"]
            self.vote_counters = db.get_vote_counter(self.food_names[0])
            self.vote_counterm = db.get_vote_counter(self.food_names[1])
            self.vote_countera = db.get_vote_counter(self.food_names[2])
            self.vote_counterd = db.get_vote_counter(self.food_names[3])
            return True
        else:
            return False

    def get_food_calories(self):
        self.food_calories = []
        db = current_app.config["db"]
        for i in range(len(self.food_names)):
            self.food_calories.append(db.get_food_calorie(self.food_names[i]))
        return True

    def get_average_rates(self):
        if(self.food_names != None):
            db = current_app.config["db"]
            self.average_rates = db.get_average_rate(self.food_names[0])
            self.average_ratem = db.get_average_rate(self.food_names[1])
            self.average_ratea = db.get_average_rate(self.food_names[2])
            self.average_rated = db.get_average_rate(self.food_names[3])
            return True
        else:
            return False

    def get_meal_vote_count(self):
        db = current_app.config["db"]
        self.score_vote_count = db.get_meal_vote_count(self.id)
        return True

    def get_score(self):
        db = current_app.config["db"]
        self.score = db.get_meal_score(self.id)
        self.get_meal_vote_count()
        return True
    


    def add_database(self):
        db = current_app.config["db"]
        succesfull = db.create_meal(self)
        return succesfull
    
    def meal(self, meal_id):
        db = current_app.config["db"]
        self.food_names = db.get_meal(meal_id)
        return True

    def Itu_meal(self):
        site = "https://sks.itu.edu.tr/ExternalPages/sks/yemek-menu-v2/uzerinde-calisilan/yemek-menu.aspx?tip="
        r = requests.get(site)
        soup = BeautifulSoup(r.content, "html.parser")
        gelen_veri = soup.find_all("a",{"class":"js-nyro-modal"})
        self.food_names = []
        for yemek in gelen_veri:
            if yemek.text:
                self.food_names.append(yemek.text)
        self.food_calories = []
        for yemek in gelen_veri:
            if yemek.has_attr('href'):
                site = "https://sks.itu.edu.tr" + yemek.attrs['href']
                r = requests.get(site)
                soup = BeautifulSoup(r.content, "html.parser")
                gelen_veri = soup.find_all("div", {"class":"nutritional-values__table"})
                for a in gelen_veri:
                    for i in range(100):
                        if(a.text.rsplit(' ')[i] == "(kcal)"):
                            b = a.text.rsplit(' ')[i+1]
                            self.food_calories.append(b.rsplit('\n')[0])
                            break

        if(self.food_names != []):        
            usr.insert_food("Soup", self.food_calories[0], self.food_names[0])
            usr.insert_food("Main Course", self.food_calories[1], self.food_names[1])
            usr.insert_food("Yan Yemek", self.food_calories[2], self.food_names[2])
            usr.insert_food("Tatli", self.food_calories[3], self.food_names[3])
            self.is_read = True
            db = current_app.config["db"]
            self.food_ids = []
            self.food_ids.append(db.get_food(self.food_names[0]))
            self.food_ids.append(db.get_food(self.food_names[1]))
            self.food_ids.append(db.get_food(self.food_names[2]))
            self.food_ids.append(db.get_food(self.food_names[3])) 
            db = current_app.config["db"]
            self.add_database()
            self.id = db.get_meal_id(self.food_ids)
            return True
        else:
            self.food_names = None
            self.food_ids = None
            self.id = None
            return False