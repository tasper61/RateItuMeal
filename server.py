from flask import Flask, current_app
from flask_login import LoginManager
from user import get_user
import database
import views
import user as usr
import current_meal

lm = LoginManager()

lm.login_message = ""

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)

def create_app():  
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/profile", view_func=views.profile_page, methods=["GET","POST"])
    app.add_url_rule("/create_user", view_func=views.create_user_page, methods=["GET", "POST"])
    app.add_url_rule("/meals/<string:meal_id>", view_func=views.meal_page, methods=["GET","POST"])
    app.add_url_rule("/_give_suggestions", view_func=views.give_suggestions, methods=["POST"])
    app.add_url_rule("/proposals",view_func=views.proposals_page, methods=["GET","POST"])
    lm.init_app(app)
    lm.login_view = "login_page"
    db = database.Database() 
    app.config["db"] = db
    return app

 

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
