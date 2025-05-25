document.addEventListener('DOMContentLoaded', () => {
  const addBookForm = document.getElementById('addBookForm');
  const bookTableBody = document.querySelector('#bookTable tbody');
  const refreshBooksBtn = document.getElementById('refreshBooksBtn');

  refreshBooksBtn.addEventListener('click', fetchBooks);
  fetchBooks();

  // Add new book
  addBookForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const categoriesInput = document.getElementById('categories').value.trim();
    const categoryIds = categoriesInput
      ? categoriesInput.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
      : [];

    const data = {
      title: document.getElementById('title').value.trim(),
      author: document.getElementById('author').value.trim(),
      isbn: document.getElementById('isbn').value.trim(),
      publisher: document.getElementById('publisher').value.trim(),
      publication_year: parseInt(document.getElementById('publication_year').value.trim()) || null,
      edition: document.getElementById('edition').value.trim(),
      format: document.getElementById('format').value.trim(),
      language: document.getElementById('language').value.trim(),
      shelf_location: document.getElementById('shelf_location').value.trim(),
      copies: parseInt(document.getElementById('copies').value.trim()) || 1,
      categories: categoryIds
    };

    const res = await fetch('/api/books', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      alert('Book added successfully!');
      addBookForm.reset();
      fetchBooks();
    } else {
      const error = await res.json();
      alert('Failed to add book: ' + (error.error || 'Unknown error'));
    }
  });

  // Fetch all books
  async function fetchBooks() {
    const res = await fetch('/api/books');
    const books = await res.json();

    bookTableBody.innerHTML = '';
    books.forEach(book => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${book.metadata_id}</td>
        <td>${book.title}</td>
        <td>${book.author}</td>
        <td>${book.isbn}</td>
        <td>${book.shelf_locations.join(', ')}</td>
         `;
      bookTableBody.appendChild(row);
    });
  }

  // Expose deleteBook globally
  window.deleteBook = async (metadataId) => {
    if (!confirm('Are you sure you want to delete this book?')) return;
    const res = await fetch(`/api/books/${metadataId}`, { method: 'DELETE' });
    if (res.ok) {
      alert('Book deleted.');
      fetchBooks();
    } else {
      alert('Failed to delete book.');
    }
  };
});
