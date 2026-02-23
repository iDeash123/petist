// Tailwind CSS Configuration
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                brand: {
                    50: '#f0fdf4',
                    100: '#dcfce7',
                    500: '#22c55e',
                    600: '#16a34a',
                    700: '#15803d',
                    900: '#14532d',
                }
            },
            fontFamily: {
                sans: ['Outfit', 'sans-serif'],
            }
        }
    }
};

// Immediately check theme preference to prevent flicker
if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
} else {
    document.documentElement.classList.remove('dark');
}

document.addEventListener('DOMContentLoaded', () => {
    // CSRF token for HTMX requests
    document.body.addEventListener('htmx:configRequest', (event) => {
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            event.detail.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
        }
    });

    // Close modal on successful authentication (when HX-Redirect is received)
    document.body.addEventListener('htmx:beforeSwap', (event) => {
        if (event.detail.xhr.getResponseHeader('HX-Redirect')) {
            // Dispatch event to close modal
            window.dispatchEvent(new CustomEvent('close-auth-modal'));
        }
    });
});
