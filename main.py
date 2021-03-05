from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired
import requests
from typing import Callable
from os import system
system('cls')

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///day64.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class EditForm(FlaskForm):
    rating = DecimalField(label = "Your Rating Out of 10", validators = [DataRequired()])
    review = StringField(label = "Your Review", validators = [DataRequired()])
    submit = SubmitField(label = "Save Changes")


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

# new_record = Movie(
#     title = "Phone Booth",
#     year = 2002,
#     description = "Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating = 7.3,
#     ranking = 10,
#     review = "My favourite character was the caller.",
#     img_url = "https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_record)
# db.session.commit()




@app.route("/")
def home():
    data = db.session.query(Movie).all()
    return render_template("index.html", movies = data)

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
    


if __name__ == '__main__':
    app.run(debug=True)
