window.onload = function () {
    fetch('/api/books')
        .then(res => res.json())
        .then(books => {
            const bookTable = document.getElementById('book-table');
            const borrowBookSelect = document.getElementById('borrowBookId');
            const returnBookSelect = document.getElementById('returnBookId');

            const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};

            borrowBookSelect.innerHTML = '<option value="">Select a Book</option>';
            returnBookSelect.innerHTML = '<option value="">Select a Book</option>';

            books.forEach(book => {
                const id = book.book_id;
                const isBorrowed = borrowingData[id] ? true : false;

                const row = document.createElement('tr');
                row.setAttribute('data-id', id);
                row.innerHTML = `
                    <td>${id}</td>
                    <td><a href="viewer.html?id=${id}" target="_blank">${book.title}</a></td>
                    <td>${book.publisher}</td>
                    <td>${book.publication_year}</td>
                    <td>${book.format}</td>
                    <td>${isBorrowed ? borrowingData[id].borrowerName : ''}</td>
                    <td>${isBorrowed ? borrowingData[id].borrowDate : ''}</td>
                    <td>${isBorrowed ? borrowingData[id].returnDate : ''}</td>
                    <td>${isBorrowed ? 'Borrowed' : 'Present'}</td>
                `;
                bookTable.appendChild(row);

                if (!isBorrowed) {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = `${id} - ${book.title}`;
                    borrowBookSelect.appendChild(option);
                } else {
                    const returnOption = document.createElement('option');
                    returnOption.value = id;
                    returnOption.textContent = `${id} - ${book.title}`;
                    returnBookSelect.appendChild(returnOption);
                }
            });
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
};

// Borrow and return logic can remain as-is (using localStorage)
