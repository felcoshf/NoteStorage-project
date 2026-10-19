document.addEventListener('DOMContentLoaded', () => {
    const editorContainer = document.getElementById('editor-container');
    if (!editorContainer || typeof Quill === 'undefined') return;

    const quill = new Quill('#editor-container', {
        theme: 'snow',
        placeholder: 'Текст заметки...',
        modules: {
            toolbar: [
                [{ header: [1, 2, 3, false] }],
                ['bold', 'italic', 'underline', 'strike'],
                [{ list: 'ordered' }, { list: 'bullet' }],
                ['image'],
                ['clean']
            ]
        }
    });
    window.quill = quill;

    const form = document.getElementById('note-form') || editorContainer.closest('form');
    const hiddenInput = document.getElementById('id_content') || document.querySelector('input[name="content"]');
    if (form && hiddenInput) {
        form.addEventListener('submit', () => {
            hiddenInput.value = quill.root.innerHTML;
        });
    }
});
