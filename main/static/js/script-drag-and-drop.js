document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('notes-container');
    if (!container) return;

    const buttons = document.querySelectorAll('.category-target');
    const notes = container.querySelectorAll('.draft');

    let currentCategory = 'all';

    function filter(category) {
        currentCategory = category;
        notes.forEach(note => {
            const match = category === 'all' || note.classList.contains(`category-${category}`);
            note.style.display = match ? '' : 'none';
        });
    }

    buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();

        buttons.forEach(b => b.classList.remove('active'));

        btn.classList.add('active');

        filter(btn.dataset.category || 'all');
        });
    });

    const allBtn = document.querySelector('.category-target[data-category="all"]');
    if (allBtn) {
        buttons.forEach(b => b.classList.remove('active'));
        allBtn.classList.add('active');
        filter('all');
    }

    buttons.forEach(btn => {
        const category = btn.dataset.category;
        if (!category || category === 'all') return;

        btn.addEventListener('dragover', (e) => {
            e.preventDefault();
            btn.classList.add('drag-over');
        });

        btn.addEventListener('dragleave', () => {
            btn.classList.remove('drag-over');
        });

        btn.addEventListener('drop', async (e) => {
            e.preventDefault();
            btn.classList.remove('drag-over');

            const noteId = e.dataTransfer.getData('text/plain');
            if (!noteId) return;

            const noteEl = document.getElementById(`note-${noteId}`);
            if (!noteEl) return;

            if (noteEl.classList.contains(`category-${category}`)) return;

            try {
                const response = await fetch(`/notes/${noteId}/move/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: JSON.stringify({ category }),
                });

                const data = await response.json();
                if (!data.ok) throw new Error(data.error || 'Ошибка');

                noteEl.classList.forEach(cls => {
                    if (cls.startsWith('category-')) {
                        noteEl.classList.remove(cls);
                    }
                });
                noteEl.classList.add(`category-${category}`);

                if (currentCategory !== 'all' && currentCategory !== category) {
                    noteEl.style.display = 'none';
                }
            } catch (err) {
                console.error('Не удалось переместить заметку:', err);
                alert('Не удалось изменить категорию');
            }
        });
    });

    notes.forEach(note => {
        note.addEventListener('dragstart', (e) => {
            const id = note.id.replace('note-', '');
            e.dataTransfer.setData('text/plain', id);
            e.dataTransfer.effectAllowed = 'move';
            note.classList.add('dragging');
        });

        note.addEventListener('dragend', () => {
            note.classList.remove('dragging');
        });
    });

    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                return decodeURIComponent(c.substring(name.length + 1));
            }
        }
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : '';
    }
});