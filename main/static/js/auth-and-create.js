document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('note-form');
    const titleInput = document.getElementById('note-title');
    const hiddenContent = document.getElementById('hidden-content-input');
    const loginToCreate = document.getElementById('login-to-create');
    const authModal = document.getElementById('authModal');

    const savedTitle = localStorage.getItem('pending_note_title');
    const savedContent = localStorage.getItem('pending_note_content');

    const isAuthed = !loginToCreate;

    if (isAuthed && (savedTitle || savedContent)) {
        if (savedTitle && titleInput) titleInput.value = savedTitle;

        if (savedContent && typeof quill !== 'undefined' && quill) {
            try {
                const delta = quill.clipboard.convert({ html: savedContent });
                quill.setContents(delta, 'silent');
            } catch (e) {
                console.error('Не удалось восстановить черновик:', e);
            }
        }
    }

    if (form && loginToCreate && authModal) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            if (titleInput) {
                localStorage.setItem('pending_note_title', titleInput.value);
            }

            if (typeof quill !== 'undefined' && quill && hiddenContent) {
                hiddenContent.value = quill.root.innerHTML;
                localStorage.setItem('pending_note_content', hiddenContent.value);
            }

            authModal.classList.add('active');
        });
    }

    if (form && !loginToCreate) {
        form.addEventListener('submit', () => {
            localStorage.removeItem('pending_note_title');
            localStorage.removeItem('pending_note_content');
        });
    }
});