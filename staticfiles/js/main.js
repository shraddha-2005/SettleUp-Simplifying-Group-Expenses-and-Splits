document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

let currentPaymentData = {};

function showExpenseDetails(expenseId) {
    const modal = new bootstrap.Modal(document.getElementById('expenseModal'));
    document.getElementById('expenseModalBody').innerHTML = `
        <p><strong>Expense ID:</strong> ${expenseId}</p>
        <p>Details for this expense would be loaded here.</p>
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            This is a basic implementation. In a full application, this would show
            detailed breakdown of who owes what to whom.
        </div>
    `;
    modal.show();
}

function makePayment(paidById, paidToId, amount, paidByName, paidToName) {
    currentPaymentData = {
        paidById: paidById,
        paidToId: paidToId,
        amount: amount,
        paidByName: paidByName,
        paidToName: paidToName
    };

    const paymentDetails = document.getElementById('paymentDetails');
    paymentDetails.innerHTML = `
        <div class="text-center">
            <h6>Payment Confirmation</h6>
            <p><strong>From:</strong> ${paidByName}</p>
            <p><strong>To:</strong> ${paidToName}</p>
            <p class="h4 text-primary">Amount: ${formatCurrency(amount, 'USD', false)}</p>
        </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
    modal.show();
}

function recordPayment() {
    document.getElementById('paidById').value = currentPaymentData.paidById;
    document.getElementById('paidToId').value = currentPaymentData.paidToId;
    document.getElementById('paymentAmount').value = currentPaymentData.amount;

    const paymentDetails = document.getElementById('paymentDetails');
    paymentDetails.innerHTML = `
        <div class="payment-success text-center">
            <i class="fas fa-check-circle fa-3x mb-3"></i>
            <h5>Payment Successful!</h5>
           <p>${currentPaymentData.paidByName} paid ${formatCurrency(currentPaymentData.amount, 'USD', false)} to ${currentPaymentData.paidToName}</p>
        </div>
    `;

    setTimeout(function() {
        document.getElementById('recordPaymentForm').submit();
    }, 2000);
}

function formatCurrency(amount, currency = 'USD', showSymbol = true) {
    const options = {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    };

    if (showSymbol) {
        options.style = 'currency';
        options.currency = currency;
    }

    return new Intl.NumberFormat('en-US', options).format(amount);
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    let isValid = true;
    
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="loading"></span> Loading...';
    element.disabled = true;
    
    return function() {
        element.innerHTML = originalContent;
        element.disabled = false;
    };
}

function handleAjaxError(error) {
    console.error('AJAX Error:', error);
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <strong>Error:</strong> Something went wrong. Please try again.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').prepend(alertDiv);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
