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
    # loads all reviews from database and displays in html
    reviews = mongo.db.reviews.find()
    return render_template("reviews.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    # register a new account user and hashed pword into db
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
        return redirect(url_for("get_reviews"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # checks user and pword with db and creates session cookie
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
                return redirect(url_for("my_reviews"))
            else:
                # wrong password
                flash("Username and/or Password invalid")
                return redirect(url_for("login"))

        else:
            # wrong username
            flash("Username and/or Password invalid")
            return redirect(url_for(
                "login", username=session["current_user"]))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # clear session cookies
    flash("Logged Out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/my_reviews/")
def my_reviews():
    # gets user reviews page
    reviews = mongo.db.reviews.find()
    return render_template("my_reviews.html", reviews=reviews)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    # lets user create a new review and adds to db
    if request.method == "POST":
        review = {
            "band_name": request.form.get("band_name"),
            "venue_name": request.form.get("venue_name"),
            "city_name": request.form.get("city_name"),
            "country_name": request.form.get("country_name"),
            "show_date": request.form.get("show_date"),
            "rating": request.form.get("rating"),
            "review_content": request.form.get("review_content"),
            "created_by": session["current_user"]
        }
        mongo.db.reviews.insert_one(review)
        flash("Thanks for your review!")
        return redirect(url_for("get_reviews"))
    return render_template("add_review.html")


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    # lets user edit a review by replacing values
    if request.method == "POST":
        changes = {
            "band_name": request.form.get("band_name"),
            "venue_name": request.form.get("venue_name"),
            "city_name": request.form.get("city_name"),
            "country_name": request.form.get("country_name"),
            "show_date": request.form.get("show_date"),
            "rating": request.form.get("rating"),
            "review_content": request.form.get("review_content"),
            "created_by": session["current_user"]
        }
        mongo.db.reviews.replace_one({"_id": ObjectId(review_id)}, changes)
        flash("Successfully edited your review")
        return redirect(url_for("my_reviews"))

    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    return render_template("edit_review.html", review=review)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    # targets _id key from db to delete specific review
    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
    flash("Your Review Has Been Deleted")
    return redirect(url_for("my_reviews"))


@app.route("/search", methods=["GET", "POST"])
def search():
    # searches db index for string provided by user and displays results
    query = request.form.get("query")
    reviews = list(mongo.db.reviews.find({"$text": {"$search": query}}))
    return render_template("reviews.html", reviews=reviews)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
