document.addEventListener('DOMContentLoaded', () => {
    const totalBooksEl = document.getElementById('total-books');
    const totalBorrowersEl = document.getElementById('total-borrowers');
    const activeLoansEl = document.getElementById('active-loans');
    const overdueLoansEl = document.getElementById('overdue-loans');

    const booksTableBody = document.querySelector('#books-table tbody');
    const noResultsEl = document.getElementById('no-results');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    // Fetch and display quick stats
    async function fetchStats() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) throw new Error('Failed to fetch stats');
            const stats = await response.json();

            totalBooksEl.textContent = stats.total_books;
            totalBorrowersEl.textContent = stats.total_borrowers;
            activeLoansEl.textContent = stats.active_loans;
            overdueLoansEl.textContent = stats.overdue_loans;
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }

    // Fetch books (optionally with search filter)
    async function fetchBooks(searchTerm = '') {
        try {
            // Encode search query param
            const queryParam = searchTerm ? `?search=${encodeURIComponent(searchTerm)}` : '';
            const response = await fetch('/api/books' + queryParam);
            if (!response.ok) throw new Error('Failed to fetch books');
            const books = await response.json();

            renderBooks(books);
        } catch (error) {
            console.error('Error fetching books:', error);
            booksTableBody.innerHTML = '';
            noResultsEl.style.display = 'block';
            noResultsEl.textContent = 'Error loading books.';
        }
    }

    // Render books in table
    function renderBooks(books) {
        booksTableBody.innerHTML = '';
        if (!books.length) {
            noResultsEl.style.display = 'block';
            return;
        }
        noResultsEl.style.display = 'none';

        books.forEach(book => {
            const tr = document.createElement('tr');

            // Highlight borrowed books row
            if (book.available_copies === 0) {
                tr.classList.add('borrowed');
            }

            tr.innerHTML = `
                <td>${book.title}</td>
                <td>${book.author}</td>
                <td>${book.category_names || ''}</td>
                <td>${book.publication_year || ''}</td>
                <td>${book.available_copies}</td>
                <td>${(book.shelf_locations || []).join(', ')}</td> 
            `;
            booksTableBody.appendChild(tr);
        });
    }

    // Search button click handler
    searchBtn.addEventListener('click', () => {
        const term = searchInput.value.trim();
        fetchBooks(term);
    });

    // Enter key triggers search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });

    // Initial load
    fetchStats();
    fetchBooks();
});
