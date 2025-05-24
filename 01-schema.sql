-- CATEGORY TABLE
DROP TABLE IF EXISTS book_category, fine_transaction, loan, borrower, borrower_category, department, book_language, book_copy, book, category CASCADE;

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- BOOK METADATA (COMMON DETAILS)
CREATE TABLE book (
    metadata_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    publisher VARCHAR(100),
    isbn VARCHAR(20),
    publication_year INTEGER,
    edition VARCHAR(50),
    format VARCHAR(50)
);

-- BOOK COPY (EACH PHYSICAL COPY)
CREATE TABLE book_copy (
    book_id SERIAL PRIMARY KEY,
    metadata_id INTEGER,
    shelf_location VARCHAR(100),
    available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (metadata_id) REFERENCES book(metadata_id)
);

-- BOOK LANGUAGES
CREATE TABLE book_language (
    metadata_id INTEGER,
    language VARCHAR(50),
    PRIMARY KEY (metadata_id, language),
    FOREIGN KEY (metadata_id) REFERENCES book(metadata_id)
);

-- DEPARTMENT
CREATE TABLE department (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(100),
    contact_number VARCHAR(20)
);

-- BORROWER CATEGORY
CREATE TABLE borrower_category (
    name VARCHAR(50) PRIMARY KEY,
    requires_department BOOLEAN DEFAULT FALSE,
    max_books_allowed INTEGER,
    max_loan_period INTEGER,
    fine_rate_per_day NUMERIC(8,2)
);

-- BORROWER
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

-- LOAN
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
    FOREIGN KEY (book_id) REFERENCES book_copy(book_id)
);

-- FINE TRANSACTION
CREATE TABLE fine_transaction (
    transaction_id SERIAL PRIMARY KEY,
    loan_id INTEGER,
    amount NUMERIC(8,2),
    payment_date DATE,
    payment_method VARCHAR(50),
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
);

-- BOOK CATEGORY (MANY-TO-MANY: METADATA ↔ CATEGORY)
CREATE TABLE book_category (
    metadata_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (metadata_id, category_id),
    FOREIGN KEY (metadata_id) REFERENCES book(metadata_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);
