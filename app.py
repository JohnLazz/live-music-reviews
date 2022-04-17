import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
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
@app.route("/get_reviews")
def get_reviews():
    reviews = mongo.db.reviews.find()
    return render_template("reviews.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check for existing username
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username taken, try something else")
            return redirect(url_for('register'))

        new_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(
                request.form.get("password").lower())
        }
        mongo.db.users.insert_one(new_user)

        # create session cookie
        session["current_user"] = request.form.get("username").lower()
        flash("Great, your new account is good to go!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check for existing username
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check password hash
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["current_user"] = request.form.get(
                        "username").lower()
            else:
                # wrong password
                flash("Username and/or Password invalid")
                return redirect(url_for("login"))

        else:
            # wrong username
            flash("Username and/or Password invalid")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
