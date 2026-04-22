function applySavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    const icon = document.getElementById('themeIcon');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    if (icon) icon.innerText = '☀️';
    } else {
        document.body.classList.remove('dark-mode');
        if (icon) icon.innerText = '🌙';
    }
}
window.addEventListener('DOMContentLoaded', applySavedTheme);