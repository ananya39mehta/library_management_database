from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date, timedelta, datetime
import os
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from decimal import Decimal
from sqlalchemy import text
import traceback

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://lms:lms123@localhost:5433/library'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Many-to-many with Book via book_category association table
    books = db.relationship(
        'Book',
        secondary='book_category',
        back_populates='categories'
    )

class Book(db.Model):
    __tablename__ = 'book'  # book metadata table
    metadata_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    publication_year = db.Column(db.Integer)
    edition = db.Column(db.String(50))
    format = db.Column(db.String(50))

    # One-to-many: copies and languages
    copies = db.relationship('BookCopy', backref='book', lazy=True)
    languages = db.relationship('BookLanguage', backref='book', lazy=True)

    # Many-to-many with categories
    categories = db.relationship(
        'Category',
        secondary='book_category',
        back_populates='books'
    )

class BookCopy(db.Model):
    __tablename__ = 'book_copy'
    book_id = db.Column(db.Integer, primary_key=True)  # unique copy id
    metadata_id = db.Column(db.Integer, db.ForeignKey('book.metadata_id'))
    shelf_location = db.Column(db.String(100))
    available = db.Column(db.Boolean, default=True)

class BookLanguage(db.Model):
    __tablename__ = 'book_language'
    metadata_id = db.Column(db.Integer, db.ForeignKey('book.metadata_id'), primary_key=True)
    language = db.Column(db.String(50), primary_key=True)

class Department(db.Model):
    __tablename__ = 'department'
    dept_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))

    borrowers = db.relationship('Borrower', backref='department', lazy=True)

class BorrowerCategory(db.Model):
    __tablename__ = 'borrower_category'
    name = db.Column(db.String(50), primary_key=True)
    requires_department = db.Column(db.Boolean, default=False)
    max_books_allowed = db.Column(db.Integer)
    max_loan_period = db.Column(db.Integer)
    fine_rate_per_day = db.Column(db.Numeric(8, 2))

    borrowers = db.relationship('Borrower', backref='category', lazy=True)

class Borrower(db.Model):
    __tablename__ = 'borrower'
    borrower_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    registration_date = db.Column(db.Date)
    total_fines_due = db.Column(db.Numeric(10, 2), default=0)

    category_id = db.Column(db.String(50), db.ForeignKey('borrower_category.name'))
    dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'))

    loans = db.relationship('Loan', backref='borrower', lazy=True)

class Loan(db.Model):
    __tablename__ = 'loan'
    loan_id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.borrower_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book_copy.book_id'), nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    format_borrowed = db.Column(db.String(50))
    fine_amount = db.Column(db.Numeric(8, 2), default=0)
    status = db.Column(db.String(50), nullable=False)

    fine_transactions = db.relationship('FineTransaction', backref='loan', lazy=True)

class FineTransaction(db.Model):
    __tablename__ = 'fine_transaction'
    transaction_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.loan_id'))
    amount = db.Column(db.Numeric(8, 2))
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))

class BookCategory(db.Model):
    __tablename__ = 'book_category'
    metadata_id = db.Column(db.Integer, db.ForeignKey('book.metadata_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)

# Routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

@app.route('/borrower_management')
def borrower_management():
    return render_template('borrower_management.html')

@app.route('/book_management')
def book_management():
    return render_template('book_management.html')

@app.route('/loan_fine')
def loan_fine_management():
    return render_template('loan_fine.html')

# ---Route : Dispaly the book Catelog 
@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        search_term = request.args.get('search', '').strip()

        query = Book.query.options(
            db.joinedload(Book.languages),
            db.joinedload(Book.categories),
            db.joinedload(Book.copies)
        )

        if search_term:
            # Explicitly join via association table if many-to-many
            query = query.join(Book.categories).filter(
                db.or_(
                    Book.title.ilike(f'%{search_term}%'),
                    Book.author.ilike(f'%{search_term}%'),
                    Category.name.ilike(f'%{search_term}%')
                )
            ).distinct()

        books = query.all()

        # Collect all book copy IDs for active loan check
        copy_ids = [copy.book_id for book in books for copy in book.copies]

        active_loans = Loan.query.filter(
            Loan.book_id.in_(copy_ids),
            Loan.return_date.is_(None)
        ).all()

        loans_dict = {}
        for loan in active_loans:
            loans_dict.setdefault(loan.book_id, []).append(loan)

        books_data = []
        for book in books:
            shelf_locations = list({copy.shelf_location for copy in book.copies})

            active_loans_for_book = []
            for copy in book.copies:
                active_loans_for_book.extend(loans_dict.get(copy.book_id, []))

            active_count = len(active_loans_for_book)
            active_loan = active_loans_for_book[0] if active_loans_for_book else None

            books_data.append({
                'metadata_id': book.metadata_id,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher,
                'isbn': book.isbn,
                'publication_year': book.publication_year,
                'edition': book.edition,
                'format': book.format,
                'languages': [lang.language for lang in book.languages],
                'shelf_locations': shelf_locations,
                'total_copies': len(book.copies),
                'available_copies': len(book.copies) - active_count,
                'category_names': [cat.name for cat in book.categories],
                'borrower_name': active_loan.borrower.name if active_loan and active_loan.borrower else None,
                'borrow_date': active_loan.checkout_date.isoformat() if active_loan else None,
                'return_date': active_loan.return_date.isoformat() if active_loan and active_loan.return_date else None,
                'borrowed_by_current_user': False
            })

        return jsonify(books_data)

    except Exception as e:
        
        traceback.print_exc()
        app.logger.error(f"Error loading books: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_books = db.session.query(BookCopy).count()
        total_borrowers = db.session.query(Borrower).count()
        active_loans = db.session.query(Loan).filter(Loan.return_date == None).count()
        overdue_loans = db.session.query(Loan).filter(
            Loan.return_date == None,
            Loan.due_date < date.today()
        ).count()

        return jsonify({
            "total_books": total_books,
            "total_borrowers": total_borrowers,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans
        })

    except Exception as e:
       
        traceback.print_exc()
        app.logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# __________________UNUSED ________________________________
# Route to add new book in the database 
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()

    # Required fields
    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn')
    copies = int(data.get('copies', 1))

    # Optional metadata
    publisher = data.get('publisher')
    publication_year = data.get('publication_year')
    edition = data.get('edition')
    format_ = data.get('format')
    shelf_location = data.get('shelf_location', 'General')

    # Optional relational data
    language = data.get('language')
    categories = data.get('categories', [])  # Expecting list of category_ids

    if not title or not isbn:
        return jsonify({'error': 'Title and ISBN are required'}), 400

    try:
        # Step 1: Check for existing metadata by ISBN
        metadata = db.session.execute(
            text("SELECT metadata_id FROM book WHERE isbn = :isbn"),
            {'isbn': isbn}
        ).fetchone()

        if metadata:
            metadata_id = metadata[0]
        else:
            # Insert into book (metadata)
            result = db.session.execute(text("""
                INSERT INTO book (title, author, publisher, isbn, publication_year, edition, format)
                VALUES (:title, :author, :publisher, :isbn, :year, :edition, :format)
                RETURNING metadata_id
            """), {
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'year': publication_year,
                'edition': edition,
                'format': format_
            })
            metadata_id = result.scalar()

        # Step 2: Insert into book_copy
        for _ in range(copies):
            db.session.execute(text("""
                INSERT INTO book_copy (metadata_id, shelf_location)
                VALUES (:metadata_id, :shelf_location)
            """), {'metadata_id': metadata_id, 'shelf_location': shelf_location})

        # Step 3: Insert into book_language if provided
        if language:
            db.session.execute(text("""
                INSERT INTO book_language (metadata_id, language)
                VALUES (:metadata_id, :language)
                ON CONFLICT DO NOTHING
            """), {'metadata_id': metadata_id, 'language': language})

        # Step 4: Insert into book_category if provided
        for category_id in categories:
            db.session.execute(text("""
                INSERT INTO book_category (metadata_id, category_id)
                VALUES (:metadata_id, :category_id)
                ON CONFLICT DO NOTHING
            """), {'metadata_id': metadata_id, 'category_id': category_id})

        db.session.commit()
        return jsonify({'message': f'{copies} copies added successfully.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        borrower_id = data.get('borrower_id')
        borrow_date = datetime.strptime(data.get('borrow_date'), '%Y-%m-%d').date()

        # Debug print input values
        print(f"[DEBUG] Borrowing book_id: {book_id}, borrower_id: {borrower_id}, borrow_date: {borrow_date}")

        borrower = Borrower.query.get(borrower_id)
        if not borrower:
            return jsonify({'message': 'Borrower not found'}), 404

        book_copy = BookCopy.query.get(book_id)
        if not book_copy:
            return jsonify({'message': 'Book copy not found'}), 400
        if not book_copy.available:
            return jsonify({'message': 'Book copy is not available'}), 400

        max_loan_period = borrower.category.max_loan_period or 14
        due_date = borrow_date + timedelta(days=max_loan_period)

        loan = Loan(
            borrower_id=borrower_id,
            book_id=book_id,
            checkout_date=borrow_date,
            due_date=due_date,
            status='borrowed',
            format_borrowed=book_copy.book.format if book_copy.book else 'Unknown'
        )

        book_copy.available = False
        db.session.add(loan)
        db.session.commit()

        return jsonify({'message': 'Book borrowed successfully!'}), 200

    except Exception as e:
        print(f"[ERROR] Borrow failed: {e}")
        return jsonify({'message': 'An error occurred while borrowing the book.'}), 500

# Route to return book 
@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.get_json()
    book_id = data.get('book_id')  # exact book copy
    borrower_id = data.get('borrower_id')
    return_date = datetime.strptime(data.get('return_date'), '%Y-%m-%d').date()

    loan = Loan.query.filter_by(
        book_id=book_id,
        borrower_id=borrower_id,
        status='borrowed',
        return_date=None
    ).first()

    if not loan:
        return jsonify({'message': 'No active loan found for this book and borrower.'}), 404

    loan.return_date = return_date
    loan.status = 'returned'

    # Make book available again
    book_copy = BookCopy.query.get(book_id)
    if book_copy:
        book_copy.available = True

    # Fine calculation
    # Check for overdue and calculate fine
    overdue_days = (return_date - loan.due_date).days
    if overdue_days > 0:
        fine_rate = loan.borrower.category.fine_rate_per_day or Decimal('0')
        fine = Decimal(str(fine_rate)) * Decimal(overdue_days)
        loan.fine_amount = fine
        loan.borrower.total_fines_due += fine

    db.session.commit()
    return jsonify({'message': 'Book returned successfully!'}), 200

# ---Route : Get borrower Info by ID
@app.route('/api/borrowers/<int:borrower_id>', methods=['GET'])
def get_borrower_by_id(borrower_id):
    try:
        borrower = Borrower.query.get(borrower_id)
        if not borrower:
            return jsonify({'error': 'Borrower not found'}), 404

        # --- Current active loans (not returned) ---
        current_loans_query = Loan.query.filter_by(borrower_id=borrower_id, return_date=None).all()
        current_loans = []
        for loan in current_loans_query:
            book_copy = BookCopy.query.get(loan.book_id)
            book_metadata = Book.query.get(book_copy.metadata_id) if book_copy else None
            current_loans.append({
                'book_title': book_metadata.title if book_metadata else 'Unknown',
                'issue_date': loan.checkout_date.strftime('%Y-%m-%d'),
                'due_date': loan.due_date.strftime('%Y-%m-%d'),
                'format_borrowed': loan.format_borrowed,
                'status': loan.status
            })

        # --- Total fines logic ---
        loans_with_fines = Loan.query.filter(
            Loan.borrower_id == borrower_id,
            Loan.fine_amount > 0
        ).all()

        total_fines = sum([float(loan.fine_amount or 0) for loan in loans_with_fines])

        paid_fines = db.session.query(
            db.func.coalesce(db.func.sum(FineTransaction.amount), 0)
        ).filter(
            FineTransaction.loan_id.in_([loan.loan_id for loan in loans_with_fines])
        ).scalar()

        total_fines_due = float(total_fines) - float(paid_fines or 0)

        # --- Fine payment history ---
        fine_payments_query = FineTransaction.query.filter(
            FineTransaction.loan_id.in_([loan.loan_id for loan in loans_with_fines]),
            FineTransaction.payment_date != None
        ).order_by(FineTransaction.payment_date.desc()).all()

        fine_payments = []
        for payment in fine_payments_query:
            fine_payments.append({
                'amount': float(payment.amount),
                'date': payment.payment_date.strftime('%Y-%m-%d'),
                'payment_method': payment.payment_method
            })

        return jsonify({
            'borrower_id': borrower.borrower_id,
            'name': borrower.name,
            'email': borrower.email,
            'phone': borrower.phone,
            'address': borrower.address,
            'registered_on': borrower.registration_date.strftime('%Y-%m-%d') if borrower.registration_date else None,
            'category': borrower.category_id,
            'department': borrower.department.name if borrower.department else None,
            'total_fines_due': round(total_fines_due, 2),
            'current_loans': current_loans,
            'fine_payments': fine_payments
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

# ---Route to edit borrower---        
@app.route('/api/borrowers/<int:borrower_id>', methods=['PUT'])
def update_borrower(borrower_id):
    try:
        borrower = Borrower.query.get(borrower_id)
        if not borrower:
            return jsonify({'error': 'Borrower not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields if present in JSON
        allowed_fields = ['name', 'email', 'phone', 'address', 'category_id', 'dept_id']
        for field in allowed_fields:
            if field in data:
                setattr(borrower, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': 'Borrower info updated successfully'})
    
    except Exception as e:
        
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.route('/api/fines/pay', methods=['POST'])
def record_fine_payment():
    try:
        data = request.get_json()
        loan_id = data.get('loan_id')
        amount = data.get('amount')
        payment_method = data.get('payment_method', 'unknown')
        payment_date = data.get('payment_date')  # optional, 'YYYY-MM-DD'

        if not loan_id or amount is None:
            return jsonify({'error': 'loan_id and amount are required'}), 400

        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'error': 'Loan not found'}), 404

        payment_amount = Decimal(str(amount))
        if payment_amount <= 0:
            return jsonify({'error': 'Payment amount must be positive'}), 400

        current_fine = loan.fine_amount or Decimal('0')

        if payment_amount > current_fine:
            return jsonify({'error': f'Payment exceeds current fine amount ({current_fine})'}), 400

        payment_dt = datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else date.today()

        fine_payment = FineTransaction(
            loan_id=loan_id,
            amount=payment_amount,
            payment_date=payment_dt,
            payment_method=payment_method
        )
        db.session.add(fine_payment)

        loan.fine_amount = current_fine - payment_amount

        if loan.fine_amount <= 0:
            loan.status = 'Fine Paid'

        borrower = loan.borrower
        total_fines = sum([l.fine_amount or Decimal('0') for l in borrower.loans])
        borrower.total_fines_due = total_fines

        db.session.commit()

        return jsonify({
            'message': 'Fine payment recorded successfully',
            'remaining_fine': str(loan.fine_amount),
            'loan_status': loan.status,
            'borrower_total_fines_due': str(borrower.total_fines_due)
        })

    except Exception as e:
        
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

# =========================================================

# Route to list borrowers
@app.route('/api/borrowers', methods=['GET'])
def get_borrowers():
    borrowers = Borrower.query.all()
    borrowers_data = []
    for b in borrowers:
        borrowers_data.append({
            'borrower_id': b.borrower_id,
            'name': b.name,
            'email': b.email,
            'phone': b.phone,
            'address': b.address,
            'registration_date': b.registration_date.isoformat() if b.registration_date else None,
            'total_fines_due': float(b.total_fines_due or 0),
            'category_id': b.category_id,
            'category_name': b.category.name if b.category else None,
            'department': b.department.name if b.department else None
        })
    return jsonify(borrowers_data)

@app.route('/api/borrowers', methods=['POST'])
def add_borrower():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    category_id = data.get('category_id')
    dept_id = data.get('dept_id')

    if not name or not email or not category_id:
        return jsonify({'message': 'Missing required fields'}), 400

    if Borrower.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    new_borrower = Borrower(
        name=name,
        email=email,
        phone=phone,
        address=address,
        category_id=category_id,
        dept_id=dept_id if dept_id else None,
        registration_date=datetime.today()
    )

    db.session.add(new_borrower)
    db.session.commit()

    return jsonify({'message': 'Borrower added', 'borrower_id': new_borrower.borrower_id}), 201



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
