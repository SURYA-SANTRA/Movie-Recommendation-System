from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import pandas as pd

from database import db, User

app = Flask(__name__)
app.secret_key = "movie_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Load data
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open("similarity.pkl", "rb"))


# Recommendation function
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []

    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies

@app.route("/")
def index():

    if "user" in session:
        return redirect(url_for("home"))

    return redirect(url_for("login"))

@app.route("/home", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect(url_for("login"))

    recommendations = []
    selected_movie = ""

    if request.method == "POST":
        selected_movie = request.form["movie"].strip()

        if selected_movie in movies["title"].values:
            recommendations = recommend(selected_movie)
        else:
            recommendations = ["❌ Movie not found in our database."]

    return render_template(
        "index.html",
        movies=movies["title"].values,
        recommendations=recommendations,
    )


@app.route("/about")
def about():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("about.html")


@app.route("/contact")
def contact():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session["user"] = user.email
            return redirect(url_for("home"))

        return "Invalid Email or Password"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists!"

        new_user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session["user"]).first()

    return render_template("profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)