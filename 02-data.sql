-- Categories
INSERT INTO category (name, description) VALUES
('Fiction', 'Fictional novels and literature'),
('Science', 'Scientific literature and research'),
('History', 'Historical texts and documents'),
('Technology', 'Technology and IT books'),
('Philosophy', 'Books on philosophy and thinking'),
('Children', 'Books for children and early readers');

-- Books
INSERT INTO book (title, author, publisher, isbn, publication_year, edition, format, shelf_location, total_copies, available_copies, category_id) VALUES
('1984', 'George Orwell', 'Secker & Warburg', '9780451524935', 1949, '1st', 'Hardcover', 'F1', 4, 3, 1),
('The Selfish Gene', 'Richard Dawkins', 'Oxford University Press', '9780198788607', 1976, '2nd', 'Paperback', 'S2', 3, 2, 2),
('Guns, Germs, and Steel', 'Jared Diamond', 'W. W. Norton & Company', '9780393317558', 1997, '1st', 'Paperback', 'H1', 2, 2, 3),
('Clean Code', 'Robert C. Martin', 'Prentice Hall', '9780132350884', 2008, '1st', 'Hardcover', 'T3', 6, 4, 4),
('Meditations', 'Marcus Aurelius', 'Penguin Classics', '9780140449334', 180, 'Modern', 'Paperback', 'P1', 5, 5, 5),
('Harry Potter and the Sorcerer Stone', 'J.K. Rowling', 'Bloomsbury', '9780747532699', 1997, '1st', 'Hardcover', 'C1', 10, 8, 6);

-- Book Languages
INSERT INTO book_language (book_id, language) VALUES
(1, 'English'), (1, 'Spanish'),
(2, 'English'),
(3, 'English'),
(4, 'English'), (4, 'German'),
(5, 'English'), (5, 'Greek'),
(6, 'English'), (6, 'French');

-- Departments
INSERT INTO department (name, building, contact_number) VALUES
('Computer Science', 'Tech Building', '111-222-3333'),
('Physics', 'Science Hall', '222-333-4444'),
('History', 'Old Main', '333-444-5555'),
('Philosophy', 'Humanities Hall', '444-555-6666');

-- Borrower Categories
INSERT INTO borrower_category (name, requires_department, max_books_allowed, max_loan_period, fine_rate_per_day) VALUES
('Student', TRUE, 5, 14, 0.50),
('Faculty', TRUE, 10, 30, 0.10),
('Visitor', FALSE, 2, 7, 1.00),
('Researcher', TRUE, 7, 21, 0.25);

-- Borrowers
INSERT INTO borrower (name, email, phone, address, registration_date, category_id, dept_id) VALUES
('Alice Johnson', 'alicej@univ.edu', '555-101-2020', '12 University St', '2025-01-12', 'Student', 1),
('Dr. Robert Lee', 'rlee@univ.edu', '555-111-2222', 'Faculty Apartments', '2024-09-01', 'Faculty', 2),
('Megan Smith', 'msmith@univ.edu', '555-123-4567', 'Research Dorm', '2025-02-20', 'Researcher', 3),
('Tom Guest', 'tom.guest@example.com', '555-555-5555', '1234 Guest House', '2025-04-01', 'Visitor', NULL),
('Sophia Kim', 'sophiak@univ.edu', '555-999-8888', 'Graduate Hall', '2025-03-15', 'Student', 4);

-- Loans
INSERT INTO loan (borrower_id, book_id, checkout_date, due_date, return_date, format_borrowed, fine_amount, status) VALUES
(1, 1, '2025-05-01', '2025-05-15', NULL, 'Hardcover', 0, 'Borrowed'),
(2, 2, '2025-04-05', '2025-05-05', '2025-05-02', 'Paperback', 0, 'Returned'),
(3, 4, '2025-05-10', '2025-05-31', NULL, 'Hardcover', 0, 'Borrowed'),
(4, 6, '2025-05-01', '2025-05-08', NULL, 'Hardcover', 2.00, 'Overdue'),
(5, 5, '2025-05-12', '2025-05-26', NULL, 'Paperback', 0, 'Borrowed');

-- Fine Transactions
INSERT INTO fine_transaction (loan_id, amount, payment_date, payment_method) VALUES
(4, 2.00, '2025-05-15', 'Cash');

-- Book Categories (many-to-many relationships)
INSERT INTO book_category (book_id, category_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 1), (6, 6);  -- Harry Potter in Fiction and Children
