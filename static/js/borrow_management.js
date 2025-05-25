document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('addBorrowerForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const newBorrower = {
          name: document.getElementById('newBorrowerName').value,
          email: document.getElementById('newBorrowerEmail').value,
          phone: document.getElementById('newBorrowerPhone').value,
          address: document.getElementById('newBorrowerAddress').value,
          category_id: document.getElementById('newBorrowerCategory').value,
          dept_id: document.getElementById('newBorrowerDeptId').value || null
        };

        try {
          const category = document.getElementById('newBorrowerCategory').value;
            if (!['Student', 'Faculty', 'Visitor', 'Researcher'].includes(category)) {
              alert('Please select a valid category.');
              return;
            }

          const res = await fetch('/api/borrowers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newBorrower)
          });

          const result = await res.json();

          if (res.ok) {
            alert(`Borrower added with ID: ${result.borrower_id}`);
            document.getElementById('addBorrowerForm').reset();
          } else {
            alert(`Error: ${result.message || 'Could not add borrower'}`);
          }
        } catch (err) {
          console.error(err);
          alert('An error occurred while adding the borrower.');
        }
      });
  const fetchBtn = document.getElementById('searchBorrowerBtn');
  const borrowerInput = document.getElementById('borrowerIdInput');

  if (!fetchBtn || !borrowerInput) {
    console.error('Required elements not found in the DOM');
    return;
  }

  let currentBorrowerId = null; // Store current borrowerId for reuse

  fetchBtn.addEventListener('click', async () => {
    const borrowerId = borrowerInput.value.trim();
    if (!borrowerId) {
      alert('Please enter a borrower ID.');
      return;
    }

    try {
      console.log('Fetching borrower with ID:', borrowerId);
      const res = await fetch(`/api/borrowers/${borrowerId}`);
      if (!res.ok) {
        alert('Borrower not found');
        return;
      }
      const data = await res.json();

      currentBorrowerId = borrowerId;

      // Show borrower details section
      const borrowerDetailsSection = document.getElementById('borrowerDetails');
      if (borrowerDetailsSection) {
        borrowerDetailsSection.style.display = 'block';
      }

      // Fill borrower info (DISPLAY & INPUTS)
      document.getElementById('borrowerNameDisplay').textContent = data.name || '-';
      document.getElementById('borrowerEmailDisplay').textContent = data.email || '-';
      document.getElementById('borrowerPhoneDisplay').textContent = data.phone || '-';
      document.getElementById('borrowerDepartmentDisplay').textContent = data.department || '-';

      document.getElementById('borrowerName').value = data.name || '';
      document.getElementById('borrowerEmail').value = data.email || '';
      document.getElementById('borrowerPhone').value = data.phone || '';
      document.getElementById('borrowerDepartment').value = data.department || '';
      document.getElementById('borrowerRegistered').textContent = data.registered_on || '-';

      // Fill current loans table
      const loansTbody = document.querySelector('#currentLoansTable tbody');
      loansTbody.innerHTML = '';
      if (data.current_loans && data.current_loans.length > 0) {
        data.current_loans.forEach(loan => {
          const tr = document.createElement('tr');
          const status = (new Date(loan.due_date) < new Date()) ? 'Overdue' : 'On Time';

          tr.innerHTML = `
            <td>${loan.book_title}</td>
            <td>${loan.issue_date}</td>
            <td>${loan.due_date}</td>
            <td>${status}</td>
          `;
          loansTbody.appendChild(tr);
        });
      } else {
        loansTbody.innerHTML = '<tr><td colspan="4">No current loans</td></tr>';
      }

      // Fines
      document.getElementById('totalFines').textContent = data.total_fines_due || '0';

      // Fine payment history
      const fineHistoryUl = document.getElementById('finePaymentHistory');
      fineHistoryUl.innerHTML = '';
      if (data.fine_payments && data.fine_payments.length > 0) {
        data.fine_payments.forEach(payment => {
          const li = document.createElement('li');
          li.textContent = `₹${payment.amount} paid on ${payment.date}`;
          fineHistoryUl.appendChild(li);
        });
      } else {
        fineHistoryUl.innerHTML = '<li>No payments recorded</li>';
      }

    } catch (err) {
      console.error('Error fetching borrower:', err);
      alert('Failed to fetch borrower data');
    }
  });

  // EDIT BORROWER HANDLER
  document.getElementById('editBorrowerBtn').addEventListener('click', () => {
    if (!currentBorrowerId) {
      alert('Search for a borrower first.');
      return;
    }

    const name = document.getElementById('borrowerName').value;
    const email = document.getElementById('borrowerEmail').value;
    const phone = document.getElementById('borrowerPhone').value;
    const dept = document.getElementById('borrowerDepartment').value;

    const data = {
      name: name,
      email: email,
      phone: phone,
      department: dept
    };

    fetch(`/api/borrowers/${currentBorrowerId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert('Error: ' + data.error);
        } else {
          alert('Borrower info updated successfully!');
          // Optionally refresh displayed info
          document.getElementById('borrowerNameDisplay').textContent = name;
          document.getElementById('borrowerEmailDisplay').textContent = email;
          document.getElementById('borrowerPhoneDisplay').textContent = phone;
          document.getElementById('borrowerDepartmentDisplay').textContent = dept;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to update borrower info');
      });
  });

  // PAY FINE HANDLER
  document.getElementById('recordFinePaymentBtn').addEventListener('click', () => {
    const loanId = document.getElementById('fineLoanId').value;
    const amount = parseFloat(document.getElementById('fineAmount').value);
    const paymentMethod = document.getElementById('finePaymentMethod').value;

    if (!loanId || isNaN(amount) || amount <= 0) {
      alert('Please enter valid loan ID and payment amount');
      return;
    }

    const data = {
      loan_id: loanId,
      amount: amount,
      payment_method: paymentMethod
    };

    fetch('/api/fines/pay', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert('Error: ' + data.error);
        } else {
          alert('Fine payment recorded! Remaining fine: ₹' + data.remaining_fine);
          // Optionally refresh borrower data
          document.getElementById('totalFines').textContent = data.remaining_fine;
          const fineHistoryUl = document.getElementById('finePaymentHistory');
          const li = document.createElement('li');
          li.textContent = `₹${amount} paid just now via ${paymentMethod}`;
          fineHistoryUl.appendChild(li);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to record fine payment');
      });
  });

});
