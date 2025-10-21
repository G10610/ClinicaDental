// static/js/theme-switcher.js

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    // Buscamos el ícono DENTRO del botón
    const themeIcon = themeToggleBtn.querySelector('i');
    const htmlElement = document.documentElement;

    // Clases de los iconos que vamos a intercambiar
    const iconDark = 'bi-moon-stars-fill';
    const iconLight = 'bi-sun-fill';

    const applyStoredTheme = () => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme === 'dark') {
            htmlElement.setAttribute('data-theme', 'dark');
            themeIcon.classList.remove(iconDark);
            themeIcon.classList.add(iconLight);
        } else {
            htmlElement.removeAttribute('data-theme');
            themeIcon.classList.remove(iconLight);
            themeIcon.classList.add(iconDark);
        }
    };

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            localStorage.removeItem('theme');
        } else {
            localStorage.setItem('theme', 'dark');
        }
        applyStoredTheme();
    });

    applyStoredTheme();
});