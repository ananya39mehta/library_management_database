-- Enable foreign key checks (enabled by default in PostgreSQL)
-- No need for PRAGMA like in SQLite

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    publisher VARCHAR(100),
    isbn VARCHAR(20),
    publication_year INTEGER,
    edition VARCHAR(50),
    format VARCHAR(50),
    shelf_location VARCHAR(100),
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);

CREATE TABLE book_language (
    book_id INTEGER,
    language VARCHAR(50),
    PRIMARY KEY (book_id, language),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);

CREATE TABLE department (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(100),
    contact_number VARCHAR(20)
);

CREATE TABLE borrower_category (
    name VARCHAR(50) PRIMARY KEY,
    requires_department BOOLEAN DEFAULT FALSE,
    max_books_allowed INTEGER,
    max_loan_period INTEGER,
    fine_rate_per_day NUMERIC(8,2)
);

CREATE TABLE borrower (
    borrower_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(200),
    registration_date DATE,
    total_fines_due NUMERIC(10,2) DEFAULT 0,
    category_id VARCHAR(50),
    dept_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES borrower_category(name),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

CREATE TABLE loan (
    loan_id SERIAL PRIMARY KEY,
    borrower_id INTEGER,
    book_id INTEGER,
    checkout_date DATE,
    due_date DATE,
    return_date DATE,
    format_borrowed VARCHAR(50),
    fine_amount NUMERIC(8,2) DEFAULT 0,
    status VARCHAR(50),
    FOREIGN KEY (borrower_id) REFERENCES borrower(borrower_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);

CREATE TABLE fine_transaction (
    transaction_id SERIAL PRIMARY KEY,
    loan_id INTEGER,
    amount NUMERIC(8,2),
    payment_date DATE,
    payment_method VARCHAR(50),
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
);

CREATE TABLE book_category (
    book_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);
