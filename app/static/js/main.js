// Utility functions for MEXC Account Manager
document.addEventListener('DOMContentLoaded', function() {
    // Form elements for email account creation
    const generateNameCheckbox = document.getElementById('generate_name');
    const generateNameBtn = document.getElementById('generate_name_btn');
    const countrySelect = document.getElementById('country');
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const emailInput = document.getElementById('email');
    
    // Generate name when the checkbox is checked
    if (generateNameCheckbox) {
        generateNameCheckbox.addEventListener('change', function() {
            if (this.checked && countrySelect.value) {
                generateRandomName();
            }
        });
    }
    
    // Generate name when the button is clicked
    if (generateNameBtn) {
        generateNameBtn.addEventListener('click', function(e) {
            e.preventDefault();
            generateRandomName();
        });
    }
    
    // Function to generate a random name based on selected country
    function generateRandomName() {
        const country = countrySelect.value;
        
        if (!country) {
            alert('Please select a country first.');
            return;
        }
        
        // Show loading indicator
        if (generateNameBtn) {
            generateNameBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            generateNameBtn.disabled = true;
        }
        
        fetch('/api/generate-name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                country: country
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server returned ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                alert('Error generating name: ' + data.error);
                return;
            }
            
            firstNameInput.value = data.first_name;
            lastNameInput.value = data.last_name;
            
            // Always update email based on the new first and last name
            emailInput.value = data.email;
        })
        .catch(error => {
            console.error('Error generating name:', error);
            alert('Failed to generate name. Please try again.');
        })
        .finally(() => {
            // Reset button state
            if (generateNameBtn) {
                generateNameBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Generate';
                generateNameBtn.disabled = false;
            }
        });
    }
    
    // Password generation function
    function generatePassword(length = 12) {
        const lowercase = 'abcdefghijklmnopqrstuvwxyz';
        const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const numbers = '0123456789';
        const symbols = '!@#$%^&*()-_=+';
        
        const allChars = lowercase + uppercase + numbers + symbols;
        
        // Ensure at least one of each character type
        let password = '';
        password += lowercase.charAt(Math.floor(Math.random() * lowercase.length));
        password += uppercase.charAt(Math.floor(Math.random() * uppercase.length));
        password += numbers.charAt(Math.floor(Math.random() * numbers.length));
        password += symbols.charAt(Math.floor(Math.random() * symbols.length));
        
        // Fill the rest of the password
        for (let i = password.length; i < length; i++) {
            password += allChars.charAt(Math.floor(Math.random() * allChars.length));
        }
        
        // Shuffle the password
        password = password.split('').sort(() => 0.5 - Math.random()).join('');
        
        return password;
    }
    
    // Generate password button
    const generatePasswordBtn = document.getElementById('generate_password_btn');
    const passwordInput = document.getElementById('password');
    
    if (generatePasswordBtn && passwordInput) {
        generatePasswordBtn.addEventListener('click', function() {
            passwordInput.value = generatePassword();
        });
    }
    
    // If nothing is in the password field when the page loads, generate a password
    if (passwordInput && passwordInput.value === '') {
        passwordInput.value = generatePassword();
    }
    
    // Auto-generate username when email changes
    const emailSelect = document.getElementById('email_id');
    const usernameInput = document.getElementById('username');
    
    if (emailSelect && usernameInput) {
        emailSelect.addEventListener('change', function() {
            if (usernameInput.value === '' || usernameInput.getAttribute('data-auto-generated') === 'true') {
                generateUsername();
                usernameInput.setAttribute('data-auto-generated', 'true');
            }
        });
        
        // Also generate username on page load if it's empty
        if (usernameInput.value === '') {
            generateUsername();
            usernameInput.setAttribute('data-auto-generated', 'true');
        }
    }
    
    // Username generation function based on email
    function generateUsername() {
        const emailSelect = document.getElementById('email_id');
        if (!emailSelect) return;
        
        const emailOption = emailSelect.options[emailSelect.selectedIndex];
        
        if (emailOption && emailOption.text) {
            const email = emailOption.text;
            const emailParts = email.split('@');
            
            if (emailParts.length > 0) {
                // Take the username part and remove special characters
                let username = emailParts[0].replace(/[^a-zA-Z0-9]/g, '');
                
                // Add a random number to make it more unique
                username += Math.floor(Math.random() * 1000);
                
                const usernameInput = document.getElementById('username');
                if (usernameInput) {
                    usernameInput.value = username;
                }
            }
        }
    }
    
    // Check URL parameters for pre-selection
    const urlParams = new URLSearchParams(window.location.search);
    const emailId = urlParams.get('email_id');
    const referrerId = urlParams.get('referrer_id');
    
    if (emailId && emailSelect) {
        emailSelect.value = emailId;
        // Trigger change event to generate username
        emailSelect.dispatchEvent(new Event('change'));
    }
    
    if (referrerId) {
        const referrerSelect = document.getElementById('referrer_id');
        if (referrerSelect) {
            referrerSelect.value = referrerId;
        }
    }
    
    // Copy to clipboard functionality
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            copyToClipboard(textToCopy, this.getAttribute('data-label') || 'Text');
        });
    });
    
    // Global function for copying to clipboard
    window.copyToClipboard = function(text, type) {
        navigator.clipboard.writeText(text).then(() => {
            // Create a toast notification
            const toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            
            const toast = document.createElement('div');
            toast.className = 'toast show';
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            toast.innerHTML = `
                <div class="toast-header bg-success text-white">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong class="me-auto">Success</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${type} copied to clipboard!
                </div>
            `;
            
            toastContainer.appendChild(toast);
            document.body.appendChild(toastContainer);
            
            // Remove the toast after 3 seconds
            setTimeout(() => {
                document.body.removeChild(toastContainer);
            }, 3000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard. Please try again.');
        });
    };
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
});