document.addEventListener('DOMContentLoaded', () => {
    const initialEl = document.getElementById('initial-content');
    const initialHtml = initialEl ? JSON.parse(initialEl.textContent) : '';
    if (initialHtml && typeof quill !== 'undefined') {
        quill.clipboard.dangerouslyPasteHTML(initialHtml);
    }

    const formEl = document.getElementById('note-form');
    if (!formEl) return;

    formEl.addEventListener('submit', () => {
        const hiddenInput = formEl.querySelector('input[name="content"]');
        if (hiddenInput && typeof quill !== 'undefined') {
            hiddenInput.value = quill.root.innerHTML;
        }
    });
});