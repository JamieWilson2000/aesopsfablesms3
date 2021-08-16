import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# @app.route("/details")
# def get_details():
#     members = mongo.db.competition.find()
#     return render_template("details.html", members=members)


@app.route("/fables")
def fables():
    return render_template("fables.html")


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")   


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/registered")
def registered():
    return render_template("registered.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = session["user"]
    stories = mongo.db.competition.find({"username": username})

    if stories.count()== 0:
        flash("You haven't written any stories yet!!")
        flash("Head over to the competition page to submit a story!")
        return render_template("profile.html", username=username)
    else:
        return render_template(
            "profile.html", username=username, stories=stories)
        
        
        


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome {}, now you're here.....".format(
                    request.form.get("username")))
                return redirect(url_for('registered'))
            else:
                flash("Incorrect Username and/or Password!")
                return redirect(url_for('login'))
        else:
            flash("Incorrect Username and/or Password!")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/logout")
def logout():
    flash("You're logged out! Come back soon!")
    session.pop("user")
    return redirect(url_for('home'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            flash("Username already taken!")
            return redirect(url_for('register'))

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
            }
        mongo.db.users.insert_one(register)

        session['user'] = request.form.get('username')
        flash("Welcome {}, now you're here.....".format(
            request.form.get("username")))
        return render_template("registered.html")

    return render_template("register.html")


@app.route("/competition", methods=["GET", "POST"])
def competition():
    if request.method == "POST":

        # stories = mongo.db.competition.find_one()
        competition = {
        "username": session['user'],
        "storytitle": request.form.get("storytitle"),
        "story": request.form.get("story")
        }
        mongo.db.competition.insert_one(competition)

        flash("Well done {}, best of luck !!".format(session['user']))
        return redirect(url_for('profile', username=session['user']))

    return render_template("competition.html")


@app.route("/edit_story/<story_id>", methods=["GET", "POST"])
def edit_story(story_id):
    story = mongo.db.competition.find_one({"_id": ObjectId(story_id)})
    if request.method == "POST":
        
        competition = {
            "username": session['user'],
            "storytitle": request.form.get("storytitle"),
            "story": request.form.get("story")
            }
        mongo.db.competition.update({"_id": ObjectId(story_id)}, competition)
        flash("Ok {}, your changes have been saved !!".format(session['user']))
        return redirect(url_for('profile', username=session['user']))

    return render_template(
        "edit_story.html",
        username=session['user'],
        story=story)


@app.route("/delete_story/<story_id>")
def delete_story(story_id):
    mongo.db.competition.remove({"_id": ObjectId(story_id)})
    flash("Story successfully deleted")
    return redirect(url_for('profile', username=session['user']))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)
