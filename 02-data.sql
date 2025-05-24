-- CATEGORIES
INSERT INTO category (name) VALUES
('Fiction'),
('Science'),
('History'),
('Technology'),
('Philosophy'),
('Children');

-- BOOK METADATA
INSERT INTO book (title, author, publisher, isbn, publication_year, edition, format) VALUES
('1984', 'George Orwell', 'Secker & Warburg', '9780451524935', 1949, '1st', 'Hardcover'),
('The Selfish Gene', 'Richard Dawkins', 'Oxford University Press', '9780198788607', 1976, '2nd', 'Paperback'),
('Guns, Germs, and Steel', 'Jared Diamond', 'W. W. Norton & Company', '9780393317558', 1997, '1st', 'Paperback'),
('Clean Code', 'Robert C. Martin', 'Prentice Hall', '9780132350884', 2008, '1st', 'Hardcover'),
('Meditations', 'Marcus Aurelius', 'Penguin Classics', '9780140449334', 180, 'Modern', 'Paperback'),
('Harry Potter and the Sorcerer Stone', 'J.K. Rowling', 'Bloomsbury', '9780747532699', 1997, '1st', 'Hardcover');

-- BOOK COPIES
-- 1984 - 4 copies
INSERT INTO book_copy (metadata_id, shelf_location) VALUES
(1, 'F1'), (1, 'F1'), (1, 'F1'), (1, 'F1');

-- The Selfish Gene - 3 copies
INSERT INTO book_copy (metadata_id, shelf_location) VALUES
(2, 'S2'), (2, 'S2'), (2, 'S2');

-- Guns, Germs, and Steel - 2 copies
INSERT INTO book_copy (metadata_id, shelf_location) VALUES
(3, 'H1'), (3, 'H1');

-- Clean Code - 6 copies
INSERT INTO book_copy (metadata_id, shelf_location) VALUES
(4, 'T3'), (4, 'T3'), (4, 'T3'), (4, 'T3'), (4, 'T3'), (4, 'T3');

-- Meditations - 5 copies
INSERT INTO book_copy (metadata_id, shelf_location) VALUES
(5, 'P1'), (5, 'P1'), (5, 'P1'), (5, 'P1'), (5, 'P1');

-- Harry Potter - 10 copies
INSERT INTO book_copy (metadata_id, shelf_location) VALUES
(6, 'C1'), (6, 'C1'), (6, 'C1'), (6, 'C1'), (6, 'C1'),
(6, 'C1'), (6, 'C1'), (6, 'C1'), (6, 'C1'), (6, 'C1');

-- BOOK LANGUAGES
INSERT INTO book_language (metadata_id, language) VALUES
(1, 'English'), (1, 'Spanish'),
(2, 'English'),
(3, 'English'),
(4, 'English'), (4, 'German'),
(5, 'English'), (5, 'Greek'),
(6, 'English'), (6, 'French');

-- DEPARTMENTS
INSERT INTO department (name, building, contact_number) VALUES
('Computer Science', 'Tech Building', '111-222-3333'),
('Physics', 'Science Hall', '222-333-4444'),
('History', 'Old Main', '333-444-5555'),
('Philosophy', 'Humanities Hall', '444-555-6666');

-- BORROWER CATEGORIES
INSERT INTO borrower_category (name, requires_department, max_books_allowed, max_loan_period, fine_rate_per_day) VALUES
('Student', TRUE, 5, 14, 0.50),
('Faculty', TRUE, 10, 30, 0.10),
('Visitor', FALSE, 2, 7, 1.00),
('Researcher', TRUE, 7, 21, 0.25);

-- BORROWERS
INSERT INTO borrower (name, email, phone, address, registration_date, category_id, dept_id) VALUES
('Alice Johnson', 'alicej@univ.edu', '555-101-2020', '12 University St', '2025-01-12', 'Student', 1),
('Dr. Robert Lee', 'rlee@univ.edu', '555-111-2222', 'Faculty Apartments', '2024-09-01', 'Faculty', 2),
('Megan Smith', 'msmith@univ.edu', '555-123-4567', 'Research Dorm', '2025-02-20', 'Researcher', 3),
('Tom Guest', 'tom.guest@example.com', '555-555-5555', '1234 Guest House', '2025-04-01', 'Visitor', NULL),
('Sophia Kim', 'sophiak@univ.edu', '555-999-8888', 'Graduate Hall', '2025-03-15', 'Student', 4);

-- LOANS
-- For simplicity, using known book_id values: assume 1 = 1984 copy 1, 5 = Selfish Gene copy 2, etc.
INSERT INTO loan (borrower_id, book_id, checkout_date, due_date, return_date, format_borrowed, fine_amount, status) VALUES
(1, 1, '2025-05-01', '2025-05-15', NULL, 'Hardcover', 0, 'Borrowed'),
(2, 5, '2025-04-05', '2025-05-05', '2025-05-02', 'Paperback', 0, 'Returned'),
(3, 10, '2025-05-10', '2025-05-31', NULL, 'Hardcover', 0, 'Borrowed'),
(4, 24, '2025-05-01', '2025-05-08', NULL, 'Hardcover', 2.00, 'Overdue'),
(5, 20, '2025-05-12', '2025-05-26', NULL, 'Paperback', 0, 'Borrowed');

-- FINE TRANSACTIONS
INSERT INTO fine_transaction (loan_id, amount, payment_date, payment_method) VALUES
(4, 2.00, '2025-05-15', 'Cash');

-- BOOK CATEGORIES
INSERT INTO book_category (metadata_id, category_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 1), (6, 6);
