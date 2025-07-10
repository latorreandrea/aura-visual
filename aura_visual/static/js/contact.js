document.addEventListener('DOMContentLoaded', function() {
    // Select the contact form
    const contactForm = document.querySelector('.email-form');
    
    if (contactForm) {
        // Add an event listener for the form submit
        contactForm.addEventListener('submit', function(event) {
            event.preventDefault();

            // Feedback elements
            const loading = contactForm.querySelector('.loading');
            const errorMessage = contactForm.querySelector('.error-message');
            const sentMessage = contactForm.querySelector('.sent-message');
            
            // Reset feedback messages
            loading.style.display = 'block';
            errorMessage.style.display = 'none';
            sentMessage.style.display = 'none';
            
            // Remove all previous errors
            document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

            // Create a FormData object to send the data
            const formData = new FormData(contactForm);

            // Send the data using the fetch API
            fetch(contactForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Hide the loader
                loading.style.display = 'none';
                
                if (data.success) {
                    // Show the success message
                    sentMessage.style.display = 'block';

                    // Disable the submit button
                    const submitButton = contactForm.querySelector('button[type="submit"]');
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="bi bi-check-circle me-2"></i>Submitted';
                    
                    // Store submission timestamp in localStorage
                    localStorage.setItem('lastFormSubmission', Date.now());
                    
                    // Reset the form but keep it disabled
                    contactForm.reset();
                    
                    // Make all form fields readonly
                    contactForm.querySelectorAll('input, textarea').forEach(el => {
                        el.readOnly = true;
                    });

                    // Scroll to the success message
                    sentMessage.scrollIntoView({ behavior: 'smooth' });
                } else {
                    // If there are field-specific errors
                    if (data.errors) {
                        Object.keys(data.errors).forEach(field => {
                            const inputElement = contactForm.querySelector(`[name="${field}"]`);
                            if (inputElement) {
                                // Add error class
                                inputElement.classList.add('is-invalid');

                                // Create and add the error message
                                const errorFeedback = document.createElement('div');
                                errorFeedback.className = 'invalid-feedback';
                                errorFeedback.textContent = data.errors[field];
                                inputElement.parentNode.appendChild(errorFeedback);
                            }
                        });
                    } else {
                        // General error
                        errorMessage.textContent = data.message || 'An error occurred. Please try again.';
                        errorMessage.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Form submission error:', error);
                loading.style.display = 'none';
                errorMessage.textContent = 'Network error. Please try again later.';
                errorMessage.style.display = 'block';
            });
        });
    }
});