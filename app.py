from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
fake = Faker()

keywords_list = [
    'Adventure', 'Mystery', 'Science Fiction', 'Fantasy',
    'History', 'Biography', 'Horror', 'Romance', 'Thriller', 'Classic'
]

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.String(200), nullable=False)

def seed_database():
    db.create_all()
    if Book.query.count() == 0:
        books = []
        for _ in range(5000):
            books.append(Book(
                title=fake.sentence(nb_words=4).strip('.'),
                author=fake.name(),
                keywords=','.join(random.sample(keywords_list, 2))
            ))
        db.session.bulk_save_objects(books)
        db.session.commit()
        print("📚 Seeded 5000 books into database.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def get_books():
    all_books = Book.query.all()
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'keywords': b.keywords.split(',')
        } for b in all_books
    ])

@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').lower()
    books = Book.query.limit(5000).all()
    suggestions = [
        b.title for b in books
        if query in b.title.lower() or any(query in k.lower() for k in b.keywords.split(','))
    ]
    return jsonify(suggestions[:10])

if __name__ == '__main__':
    with app.app_context():
        seed_database()
    app.run(debug=True)
