from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import validators
import string
import random
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(200), nullable=False)
    shortened_url = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return f'<Url {self.original_url}>'


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html', year=datetime.now().year)


@app.route('/', methods=['POST'])
def shorten():
    original_url = request.form['url']
    if not validators.url(original_url):
        flash('Please enter a valid URL')
        return redirect(url_for('home'))
    # Check if the URL is already shortened and return the existing shortened URL
    url = Url.query.filter_by(original_url=original_url).first()
    if url:
        return render_template('home.html', shortened_url=request.host_url + url.shortened_url)
    # Generate a new shortened URL and save it to the database
    shortened_url = generate_short_url()
    while Url.query.filter_by(shortened_url=shortened_url).first():
        shortened_url = generate_short_url()
    new_url = Url(original_url=original_url, shortened_url=shortened_url)
    db.session.add(new_url)
    db.session.commit()
    return render_template('home.html', shortened_url=request.host_url + shortened_url)


def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(5))


@app.route('/history')
def history():
    urls = Url.query.all()
    return render_template('history.html', urls=urls, datetime=datetime)


@app.route('/<shortened_url>')
def redirect_to_url(shortened_url):
    """Redirect the user to the original URL for the given short URL."""
    url = Url.query.filter_by(shortened_url=shortened_url).first_or_404()
    db.session.commit()
    return redirect(url.original_url)


if __name__ == '__main__':
    app.run(debug=True)
