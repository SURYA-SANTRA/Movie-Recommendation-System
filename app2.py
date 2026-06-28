from flask import Flask, render_template, request
import pickle
import pandas as pd



app = Flask(__name__)

# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
print(movies.columns)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]

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


@app.route("/", methods=["GET", "POST"])

def home():
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


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)