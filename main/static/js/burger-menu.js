document.addEventListener('DOMContentLoaded', () => {
    const burger = document.getElementById('burger');
    const dropdown = document.getElementById('dropdown');
    if (!burger || !dropdown) return;

    burger.addEventListener('click', (event) => {
        event.stopPropagation();
        dropdown.classList.toggle('active');
        burger.classList.toggle('active');
    });

    dropdown.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            dropdown.classList.remove('active');
            burger.classList.remove('active');
        });
    });
});
