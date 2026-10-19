document.addEventListener('DOMContentLoaded', () => {
    const authBtn = document.getElementById('auth-btn');
    const authModal = document.getElementById('authModal');
    const authBtn2 = document.getElementById('login-to-create');

    if (authBtn && authModal) {
        authBtn.addEventListener('click', () => {
            authModal.style.display = 'block';
            authModal.classList.add('show');
        });
    }

    if (authModal) {
        const closeBtn = authModal.querySelector('.btn-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                authModal.style.display = 'none';
                authModal.classList.remove('show');
            });
        }
    }

    if (authBtn2 && authModal) {
        authBtn2.addEventListener('click', () => {
            authModal.style.display = 'block';
            authModal.classList.add('show');
        });
    }
});