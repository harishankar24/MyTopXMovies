from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired
import requests
from confidential import api_key
from typing import Callable
from os import system
system('cls')

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///day64.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SEARCH_MOVIE_API = "https://api.themoviedb.org/3/search/movie"

class EditForm(FlaskForm):
    rating = DecimalField(label = "Your Rating Out of 10", validators = [DataRequired()])
    review = StringField(label = "Your Review", validators = [DataRequired()])
    submit = SubmitField(label = "Save Changes")
    
class AddForm(FlaskForm):
    title = StringField(label = "Movie Title", validators = [DataRequired()])
    submit = SubmitField(label = "Add Movie")

class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Float: Callable

db = MySQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable = False)
    year = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(200), nullable = False)
    rating = db.Column(db.Float, nullable = False)
    ranking = db.Column(db.Integer, nullable = False)
    review = db.Column(db.String(70), nullable = False)
    img_url = db.Column(db.String(150), nullable = False)    
db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i   
    db.session.commit()
    return render_template("index.html", movies = all_movies)


@app.route("/edit/<mov_id>", methods = ['GET','POST'])
def edit(mov_id):
    editform = EditForm()
    movie = Movie.query.get(mov_id)
    if editform.validate_on_submit():
        movie.rating = editform.rating.data
        movie.review = editform.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form = editform, movie = movie)



@app.route("/delete/<mov_id>")   
def delete(mov_id):
    movie_to_delete = Movie.query.get(mov_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    data = db.session.query(Movie).all()
    return render_template("index.html", movies = data)



@app.route("/add", methods = ['GET','POST'])
def add():
    addform = AddForm()
    if addform.validate_on_submit():
        title = addform.title.data
        return redirect(url_for('select', title = title))
    return render_template("add.html", form = addform)



@app.route("/select/<int:id>")
@app.route("/select/<string:title>", methods = ['GET','POST'])
def select(title = '', id = 0):
    if id:
        print(f"id = {id}")
        search_movie_parameters = {
            "language": "en-US",
            "api_key":api_key
        }
        response = requests.get(url = f"https://api.themoviedb.org/3/movie/{id}", params = search_movie_parameters)
        response.raise_for_status()
        data = response.json()
        new_record = Movie(
                title = f"{data['original_title']}",
                year = f"{int(data['release_date'][0:4])}",
                description =  data['overview'][:198],
                rating = data['vote_average'],
                ranking = None,
                review = None,
                img_url =  f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        search_movie_parameters = {
            "language": "en-US",
            "query":title,
            "api_key":api_key
        }
        response = requests.get(url = SEARCH_MOVIE_API, params = search_movie_parameters)
        response.raise_for_status()
        data = response.json()["results"]
        movies = []
        for item in data:
            temp_data = {
                "id": item["id"],
                "title": item['original_title'],
                "release_date": item['release_date'],
                "description": item['overview'],
                "cover_img": item['poster_path']
            }
            movies.append(temp_data)
        return render_template("select.html", movies = movies)


    
if __name__ == '__main__':
    app.run(debug=True)
