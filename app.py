from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import datetime
from datetime import date
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from decimal import Decimal
from datetime import datetime


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

@app.route('/borrower_management.html')
def borrower_management():
    return render_template('borrower_management.html')

@app.route('/loan_fine.html')
def loan_fine_management():
    return render_template('loan_fine.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        search_term = request.args.get('search', '').strip()

        query = Book.query.options(
            db.joinedload(Book.languages),
            db.joinedload(Book.categories),  # fix: use plural 'categories'
            db.joinedload(Book.copies)       # load copies to access shelf locations
        )

        if search_term:
            query = query.join(Category, isouter=True).filter(
                db.or_(
                    Book.title.ilike(f'%{search_term}%'),
                    Book.author.ilike(f'%{search_term}%'),
                    Category.name.ilike(f'%{search_term}%')
                )
            )

        books = query.all()
        book_ids = [book.metadata_id for book in books]

        # Prefetch active loans for these copies (using book_copy.book_id)
        active_loans = Loan.query.filter(
            Loan.book_id.in_([copy.book_id for book in books for copy in book.copies]),
            Loan.return_date.is_(None)
        ).all()

        loans_dict = {}
        for loan in active_loans:
            loans_dict.setdefault(loan.book_id, []).append(loan)

        books_data = []
        for book in books:
            # Collect all shelf locations for copies of this book
            shelf_locations = list({copy.shelf_location for copy in book.copies})

            # Count active loans for this book's copies
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
                'category_names': [cat.name for cat in book.categories],  # multiple categories possible
                'borrower_name': active_loan.borrower.name if active_loan and active_loan.borrower else None,
                'borrow_date': active_loan.checkout_date.isoformat() if active_loan else None,
                'return_date': active_loan.return_date.isoformat() if active_loan and active_loan.return_date else None,
                'borrowed_by_current_user': False
            })

        return jsonify(books_data)

    except Exception as e:
        import traceback
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
        import traceback
        traceback.print_exc()
        app.logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# __________________UNUSED ________________________________
# Route to add new book in the database 
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    try:
        new_book = Book(
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn'),
            edition=data.get('edition'),
            publication_year=data.get('publication_year'),
            publisher=data.get('publisher'),
            shelf_location=data.get('shelf_location'),
            total_copies=data.get('total_copies', 1),
            available_copies=data.get('available_copies', 1),
            format=data.get('format'),
            category_id=data.get('category_id')
        )
        db.session.add(new_book)
        db.session.flush()

        languages = data.get('language')
        if languages:
            if isinstance(languages, str):
                languages = [languages]
            for lang in languages:
                db.session.add(BookLanguage(book_id=new_book.book_id, language=lang))

        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding book: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Route to Borrow Book 
@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    book_id = data.get('book_id')
    borrower_id = data.get('borrower_id')
    borrow_date_str = data.get('borrow_date')

    if not book_id or not borrower_id or not borrow_date_str:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        borrow_date = datetime.date.fromisoformat(borrow_date_str)
    except ValueError:
        return jsonify({'error': 'Invalid borrow date format'}), 400

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    if book.available_copies < 1:
        return jsonify({'error': 'No available copies'}), 400

    borrower = Borrower.query.get(borrower_id)
    if not borrower:
        return jsonify({'error': 'Borrower not found'}), 404

    # Find an available copy number for the book
    available_copy = BookCopy.query.filter_by(book_id=book.book_id, status='available').first()
    if not available_copy:
        return jsonify({'error': 'No available copies (none available in copies table)'}), 400

    max_loan_days = 14
    if borrower.category_id:
        category = BorrowerCategory.query.get(borrower.category_id)
        if category and category.max_loan_period:
            max_loan_days = category.max_loan_period
    due_date = borrow_date + datetime.timedelta(days=max_loan_days)

    new_loan = Loan(
        borrower_id=borrower_id,
        book_id=book.book_id,
        copy_number=available_copy.copy_number,
        checkout_date=borrow_date,
        due_date=due_date,
        format_borrowed=book.format,
        status='borrowed'
    )

    try:
        db.session.add(new_loan)
        # Mark copy as unavailable
        available_copy.status = 'borrowed'
        # Update available copies count
        book.available_copies -= 1

        db.session.commit()
        return jsonify({'message': 'Book borrowed successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error borrowing book: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Route to return book 
@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    loan_id = data.get('loan_id')
    return_date_str = data.get('return_date')

    if not loan_id or not return_date_str:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        return_date = datetime.date.fromisoformat(return_date_str)
    except ValueError:
        return jsonify({'error': 'Invalid return date format'}), 400

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404

    if loan.return_date:
        return jsonify({'error': 'Book already returned'}), 400

    try:
        loan.return_date = return_date
        loan.status = 'returned'

        # Update available copies of book
        book = Book.query.get(loan.book_id)
        book.available_copies += 1

        # Mark copy as available again
        book_copy = BookCopy.query.filter_by(book_id=loan.book_id, copy_number=loan.copy_number).first()
        if book_copy:
            book_copy.status = 'available'

        # Calculate fines
        if return_date > loan.due_date:
            days_late = (return_date - loan.due_date).days
            category = BorrowerCategory.query.get(loan.borrower.category_id)
            fine_rate = category.fine_rate_per_day if category else 0
            loan.fine_amount = fine_rate * days_late
            # Add to borrower's total fines
            loan.borrower.total_fines_due += loan.fine_amount

        db.session.commit()
        return jsonify({'message': 'Book returned successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error returning book: {e}")
        return jsonify({'error': 'Internal server error'}), 500
# _______________________________________________________

# ---Route : Get borrower Info by ID
@app.route('/api/borrowers/<int:borrower_id>', methods=['GET'])
def get_borrower_by_id(borrower_id):
    try:
        borrower = Borrower.query.get(borrower_id)
        if not borrower:
            return jsonify({'error': 'Borrower not found'}), 404

        # Current loans where return_date is None (not returned)
        current_loans_query = Loan.query.filter_by(borrower_id=borrower_id, return_date=None).all()
        current_loans = []
        for loan in current_loans_query:
            book_copy = BookCopy.query.get(loan.book_id)
            book_metadata = None
            if book_copy:
                book_metadata = Book.query.get(book_copy.metadata_id)

            current_loans.append({
                'book_title': book_metadata.title if book_metadata else 'Unknown',
                'checkout_date': loan.checkout_date.strftime('%Y-%m-%d') if loan.checkout_date else None,
                'due_date': loan.due_date.strftime('%Y-%m-%d') if loan.due_date else None,
                'format_borrowed': loan.format_borrowed,
                'status': loan.status
            })

        # Get all loans IDs for this borrower to filter fines
        loan_ids = [loan.loan_id for loan in Loan.query.filter_by(borrower_id=borrower_id).all()]

        # Sum of unpaid fines: fines with null payment_date
        total_fines_due = db.session.query(db.func.coalesce(db.func.sum(FineTransaction.amount), 0)).filter(
            FineTransaction.loan_id.in_(loan_ids),
            FineTransaction.payment_date == None
        ).scalar()

        # Fine payments: fines with non-null payment_date, ordered by date desc
        fine_payments_query = FineTransaction.query.filter(
            FineTransaction.loan_id.in_(loan_ids),
            FineTransaction.payment_date != None
        ).order_by(FineTransaction.payment_date.desc()).all()

        fine_payments = []
        for payment in fine_payments_query:
            fine_payments.append({
                'amount': float(payment.amount) if payment.amount else 0,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d') if payment.payment_date else None,
                'payment_method': payment.payment_method
            })

        return jsonify({
            'borrower_id': borrower.borrower_id,
            'name': borrower.name,
            'email': borrower.email,
            'phone': borrower.phone,
            'address': borrower.address,
            'registration_date': borrower.registration_date.strftime('%Y-%m-%d') if borrower.registration_date else None,
            'category': borrower.category_id,
            'department': borrower.department.name if borrower.department else None,
            'total_fines_due': float(total_fines_due),
            'current_loans': current_loans,
            'fine_payments': fine_payments
        })

    except Exception as e:
        import traceback
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
        import traceback
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

        payment_dt = datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else datetime.utcnow().date()

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
        import traceback
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

# Route to add borrower
@app.route('/api/borrowers', methods=['POST'])
def add_borrower():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    try:
        reg_date = None
        if data.get('registration_date'):
            reg_date = datetime.date.fromisoformat(data.get('registration_date'))

        new_borrower = Borrower(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            registration_date=reg_date or datetime.date.today(),
            total_fines_due=data.get('total_fines_due', 0),
            category_id=data.get('category_id'),
            dept_id=data.get('dept_id')
        )
        db.session.add(new_borrower)
        db.session.commit()
        return jsonify({'message': 'Borrower added successfully', 'borrower_id':new_borrower.borrower_id}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding borrower: {e}")
        return jsonify({'error': 'Internal server error'}), 500


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

        # Convert amount to Decimal for accurate arithmetic
        payment_amount = Decimal(str(amount))
        if payment_amount <= 0:
            return jsonify({'error': 'Payment amount must be positive'}), 400

        current_fine = loan.fine_amount or Decimal('0')

        # Prevent overpayment
        if payment_amount > current_fine:
            return jsonify({'error': f'Payment exceeds current fine amount ({current_fine})'}), 400

        from datetime import datetime
        payment_dt = datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else datetime.utcnow().date()

        # Create new fine payment record
        fine_payment = FineTransaction(
            loan_id=loan_id,
            amount=payment_amount,
            payment_date=payment_dt,
            payment_method=payment_method
        )
        db.session.add(fine_payment)

        # Deduct payment from loan's fine amount
        loan.fine_amount = current_fine - payment_amount

        # Update loan status if fine fully paid
        if loan.fine_amount <= 0:
            loan.status = 'Fine Paid'  # or any status indicating fine cleared

        # Update borrower's total fines due by recalculating sum from all loans
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
