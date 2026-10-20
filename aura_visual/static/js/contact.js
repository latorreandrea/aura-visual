document.addEventListener('DOMContentLoaded', function () {
    // Select the contact form
    const contactForm = document.querySelector('.email-form');

    if (!contactForm) {
        return;
    }

    // Feedback elements
    const loading = contactForm.querySelector('.loading');
    const errorMessage = contactForm.querySelector('.error-message');
    const sentMessage = contactForm.querySelector('.sent-message');
    const submitButton = contactForm.querySelector('button[type="submit"]');
    const csrfInput = contactForm.querySelector('input[name="csrf_token"]');

    // reCAPTCHA widget (optional: absent when no site key is configured)
    const recaptchaWidget = contactForm.querySelector('.g-recaptcha');
    const recaptchaEnabled = !!(recaptchaWidget && recaptchaWidget.dataset.sitekey);

    // One silent retry is allowed for an expired CSRF token; anything else is
    // reported to the visitor immediately.
    const MAX_SUBMIT_ATTEMPTS = 2;

    let submitted = false;

    function showError(message) {
        loading.style.display = 'none';
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function clearFieldErrors() {
        document.querySelectorAll('.invalid-feedback').forEach(function (el) { el.remove(); });
        document.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
    }

    function markFieldErrors(errors) {
        Object.keys(errors).forEach(function (field) {
            const inputElement = contactForm.querySelector('[name="' + field + '"]');
            if (!inputElement) {
                return;
            }

            inputElement.classList.add('is-invalid');

            const errorFeedback = document.createElement('div');
            errorFeedback.className = 'invalid-feedback';
            errorFeedback.textContent = errors[field];
            inputElement.parentNode.appendChild(errorFeedback);
        });
    }

    function recaptchaResponse() {
        const field = contactForm.querySelector('[name="g-recaptcha-response"]');
        return field ? field.value : '';
    }

    function resetRecaptcha() {
        if (!recaptchaEnabled || !window.grecaptcha || typeof window.grecaptcha.reset !== 'function') {
            return;
        }
        try {
            window.grecaptcha.reset();
        } catch (error) {
            console.warn('Could not reset the reCAPTCHA widget:', error);
        }
    }

    function showSuccess() {
        submitted = true;
        loading.style.display = 'none';
        sentMessage.style.display = 'block';

        // Disable the submit button
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-check-circle me-2"></i>Submitted';

        // Store submission timestamp in localStorage
        localStorage.setItem('lastFormSubmission', Date.now());

        // Reset the form but keep it disabled
        contactForm.reset();

        // Make all form fields readonly
        contactForm.querySelectorAll('input, textarea').forEach(function (el) {
            el.readOnly = true;
        });

        // Scroll to the success message
        sentMessage.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * POST the form and always resolve with JSON.
     *
     * Proxies and the platform can answer with HTML (502/503, error pages from
     * an older revision, ...). Parsing those as JSON used to throw and surface
     * as a misleading "Network error".
     */
    async function postForm() {
        const response = await fetch(contactForm.action, {
            method: 'POST',
            body: new FormData(contactForm),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        });

        const contentType = response.headers.get('content-type') || '';

        if (contentType.indexOf('application/json') !== -1) {
            return { response: response, data: await response.json() };
        }

        await response.text();
        return {
            response: response,
            data: {
                success: false,
                code: 'unexpected_response',
                message: 'The server returned an unexpected response (' + response.status + '). Please try again.'
            }
        };
    }

    function messageFor(data) {
        if (data.code === 'rate_limited') {
            return data.message || 'Too many messages have been sent from this connection. Please try again later.';
        }
        if (data.code === 'csrf') {
            return 'Your session expired. Please reload the page and try again.';
        }
        return data.message || 'An error occurred. Please try again.';
    }
    contactForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        // Guard against double submits (double click or slow network)
        if (submitted || contactForm.dataset.submitting === 'true') {
            return;
        }

        // Reset feedback messages
        loading.style.display = 'block';
        errorMessage.style.display = 'none';
        sentMessage.style.display = 'none';

        // Remove all previous errors
        clearFieldErrors();

        if (recaptchaEnabled && !recaptchaResponse()) {
            showError('Please complete the reCAPTCHA verification.');
            return;
        }

        contactForm.dataset.submitting = 'true';
        submitButton.disabled = true;

        try {
            for (let attempt = 1; attempt <= MAX_SUBMIT_ATTEMPTS; attempt += 1) {
                let payload;

                try {
                    payload = await postForm();
                } catch (networkError) {
                    console.error('Form submission error:', networkError);
                    showError('Network error. Please check your connection and try again.');
                    return;
                }

                const data = payload.data || {};

                if (data.success) {
                    showSuccess();
                    return;
                }

                // Expired CSRF token: the server replied with a replacement, so
                // retry once with it instead of dropping the visitor's input.
                if (data.code === 'csrf' && attempt < MAX_SUBMIT_ATTEMPTS) {
                    if (data.csrf_token && csrfInput) {
                        csrfInput.value = data.csrf_token;
                    }
                    continue;
                }

                // Field-specific errors
                if (data.errors) {
                    markFieldErrors(data.errors);
                }

                // The token was consumed or rejected: let the visitor solve the
                // challenge again before the next attempt.
                if (typeof data.code === 'string' && data.code.indexOf('recaptcha_failed') === 0) {
                    resetRecaptcha();
                }

                showError(messageFor(data));
                return;
            }
        } finally {
            if (!submitted) {
                loading.style.display = 'none';
                submitButton.disabled = false;
            }
            delete contactForm.dataset.submitting;
        }
    });

    // reCAPTCHA lifecycle hooks, referenced by data-expired-callback and
    // data-error-callback on the widget in contact.html.
    window.auraRecaptchaExpired = function () {
        showError('The verification expired. Please complete the reCAPTCHA challenge again.');
    };

    window.auraRecaptchaError = function () {
        showError('The verification could not be loaded. Please disable any ad-blocker and reload the page.');
    };

    // If the widget never renders (ad-blocker, blocked google.com, offline) the
    // visitor would otherwise face a silently empty space above the button.
    if (recaptchaEnabled) {
        window.setTimeout(function () {
            if (!recaptchaWidget.querySelector('iframe')) {
                showError('The verification widget could not be loaded. Please disable your ad-blocker and reload the page.');
            }
        }, 8000);
    }
});
