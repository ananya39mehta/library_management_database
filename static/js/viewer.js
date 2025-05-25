window.onload = function () {
    const params = new URLSearchParams(window.location.search);
    const bookId = params.get('id');

    if (!bookId) {
        document.getElementById('content').innerHTML = '<p>Invalid or missing book ID.</p>';
        return;
    }

    fetch(`/api/books`)
        .then(res => res.json())
        .then(books => {
            const book = books.find(b => b.metadata_id === parseInt(bookId));
            if (!book) {
                document.getElementById('content').innerHTML = '<p>Book not found.</p>';
                return;
            }

            const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};
            const borrowed = borrowingData[bookId];

            let html = `<h1>${book.title}</h1><ul>
                <li><strong>ISBN:</strong> ${book.isbn}</li>
                <li><strong>Edition:</strong> ${book.edition}</li>
                <li><strong>Publisher:</strong> ${book.publisher}</li>
                <li><strong>Publication Year:</strong> ${book.publication_year}</li>
                <li><strong>Format:</strong> ${book.format}</li>
                <li><strong>Location:</strong> ${book.shelf_location}</li>
                <li><strong>Category Id:</strong> ${book.category_id}</li>
                <li><strong>Category Name:</strong> ${book.category_name}</li>
                
                <li><strong>Language:</strong> ${book.languages}s</li>
                <li><strong>Availability:</strong> ${book.available_copies}/${book.total_copies}</li>`;

            if (borrowed) {
                html += `
                <li><strong>Borrower:</strong> ${borrowed.borrowerName}</li>
                <li><strong>Borrow Date:</strong> ${borrowed.borrowDate}</li>
                <li><strong>Return Date:</strong> ${borrowed.returnDate}</li>`;
            }

            html += `</ul><div id="description"><em>Loading description...</em></div>
                     <a href="/" class="back-link">&larr; Back to Catalog</a>`;

            document.getElementById('content').innerHTML = html;

            fetchGeminiDescription(book.title);
        })
        .catch(err => {
            console.error('Failed to fetch book data', err);
            document.getElementById('content').innerHTML = '<p>Error loading book data.</p>';
        });
};

async function fetchGeminiDescription(bookTitle) {
    try {
        const res = await fetch(`/api/description?name=${encodeURIComponent(bookTitle)}`);
        const data = await res.json();
        const descriptionHTML = marked.parse(data.description || 'No description available.');
        document.getElementById('description').innerHTML = `<h2>Description</h2>${descriptionHTML}`;
    } catch (err) {
        console.error('Gemini fetch error', err);
        document.getElementById('description').innerHTML = '<p>Error loading Gemini description.</p>';
    }
}
