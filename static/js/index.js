document.addEventListener('DOMContentLoaded', () => {
    const totalBooksEl = document.getElementById('total-books');
    const totalBorrowersEl = document.getElementById('total-borrowers');
    const activeLoansEl = document.getElementById('active-loans');
    const overdueLoansEl = document.getElementById('overdue-loans');
    const booksTableBody = document.querySelector('#books-table tbody');
    const noResultsEl = document.getElementById('no-results');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    async function fetchStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            totalBooksEl.textContent = stats.total_books;
            totalBorrowersEl.textContent = stats.total_borrowers;
            activeLoansEl.textContent = stats.active_loans;
            overdueLoansEl.textContent = stats.overdue_loans;
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    }

    async function fetchBooks(searchTerm = '') {
        try {
            const query = searchTerm ? `?search=${encodeURIComponent(searchTerm)}` : '';
            const response = await fetch('/api/books' + query);
            const books = await response.json();
            renderBooks(books);
        } catch (err) {
            console.error('Error fetching books:', err);
            booksTableBody.innerHTML = '';
            noResultsEl.style.display = 'block';
            noResultsEl.textContent = 'Error loading books.';
        }
    }

    function renderBooks(books) {
        booksTableBody.innerHTML = '';
        if (!books.length) {
            noResultsEl.style.display = 'block';
            return;
        }
        noResultsEl.style.display = 'none';
        books.forEach(book => {
            const tr = document.createElement('tr');
            if (book.available_copies === 0) {
                tr.classList.add('borrowed');
            }
            tr.innerHTML = `
                <td><a href="viewer.html?id=${book.metadata_id}" class="book-link">${book.title}</a></td>
                <td>${book.author}</td>
                <td>${book.category_names || ''}</td>
                <td>${book.publication_year || ''}</td>
                <td>${book.available_copies}</td>
                <td>${(book.shelf_locations || []).join(', ')}</td>
            `;
            booksTableBody.appendChild(tr);
        });
    }

    searchBtn.addEventListener('click', () => fetchBooks(searchInput.value.trim()));
    searchInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') searchBtn.click();
    });

    document.getElementById('borrow-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const bookId = document.getElementById('borrow-book-id').value;
        const borrowerId = document.getElementById('borrow-borrower-id').value;
        const borrowDate = document.getElementById('borrow-date').value;

        if (!bookId || !borrowerId || !borrowDate) {
            alert('Please fill in all Borrow Book fields.');
            return;
        }

        try {
            const response = await fetch('/api/borrow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    book_id: parseInt(bookId),
                    borrower_id: parseInt(borrowerId),
                    borrow_date: borrowDate
                })
            });

            let result;
            try {
                result = await response.json();
            } catch {
                result = { message: 'Unexpected server response.' };
            }

            if (response.ok) {
                alert('Book borrowed successfully!');
                e.target.reset();
                fetchStats();
                fetchBooks();
            } else {
                alert(result.message || 'Failed to borrow book.');
            }
        } catch (err) {
            console.error('Error borrowing book:', err);
            alert('Error occurred while borrowing the book.');
        }
    });

    document.getElementById('return-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const bookId = document.getElementById('return-book-id').value;
        const borrowerId = document.getElementById('return-borrower-id').value;
        const returnDate = document.getElementById('return-date').value;

        if (!bookId || !borrowerId || !returnDate) {
            alert('Please fill in all Return Book fields.');
            return;
        }

        try {
            const response = await fetch('/api/return', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    book_id: parseInt(bookId),
                    borrower_id: parseInt(borrowerId),
                    return_date: returnDate
                })
            });

            let result;
            try {
                result = await response.json();
            } catch {
                result = { message: 'Unexpected server response.' };
            }

            if (response.ok) {
                alert('Book returned successfully!');
                e.target.reset();
                fetchStats();
                fetchBooks();
            } else {
                alert(result.message || 'Failed to return book.');
            }
        } catch (err) {
            console.error('Error returning book:', err);
            alert('Error occurred while returning the book.');
        }
    });

    fetchStats();
    fetchBooks();
});
