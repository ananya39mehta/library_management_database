from flask import Flask, render_template, jsonify, request
import configparser
import requests
import logging
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# --- PostgreSQL config ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://lms:lms123@localhost:5433/library'  # fallback for local use
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    isbn = db.Column(db.String)
    edition = db.Column(db.String)
    publication_year = db.Column(db.Integer)
    publisher = db.Column(db.String)
    shelf_location = db.Column(db.String)
    available_copies = db.Column(db.Integer)
    total_copies = db.Column(db.Integer)
    format = db.Column(db.String)

# --- Logging ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# --- Gemini API Config ---
config = configparser.ConfigParser()
config.read('config.ini')
try:
    GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
    GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
    logging.info("Gemini API configuration loaded.")
except Exception as e:
    logging.error("Failed to read Gemini API config: %s", e)
    GEMINI_API_KEY = None
    GEMINI_API_URL = None

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

@app.route('/api/books')
def get_books():
    books = Book.query.all()
    data = [{
        'book_id': b.book_id,
        'title': b.title,
        'isbn': b.isbn,
        'edition': b.edition,
        'publication_year': b.publication_year,
        'publisher': b.publisher,
        'shelf_location': b.shelf_location,
        'available_copies': b.available_copies,
        'total_copies': b.total_copies,
        'format': b.format
    } for b in books]
    return jsonify(data)

@app.route('/api/description', methods=['GET'])
def get_description():
    entity_name = request.args.get('name')
    if not entity_name:
        return jsonify({'error': 'Missing entity name'}), 400
    if not GEMINI_API_URL or not GEMINI_API_KEY:
        return jsonify({'error': 'Server configuration error'}), 500

    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Provide a detailed description of '{entity_name}' "
                    "If it is a book, include information about the setting, characters, themes, key concepts, and its influence. "
                    "Do not include any concluding remarks or questions. "
                    "Do not mention any Note at the end about not including concluding remarks or questions."
                )
            }]
        }]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch description', 'status_code': response.status_code}), 500

        response_data = response.json()
        description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
        return jsonify({'description': description})

    except Exception as e:
        logging.exception("Error fetching Gemini description")
        return jsonify({'error': 'Gemini API error', 'message': str(e)}), 500

# --- Start server ---
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
