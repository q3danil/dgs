function toggleMenu() {
    document.getElementById('menuToggle').classList.toggle('active');
    document.getElementById('sideMenu').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

function toggleSubmenu() {
    document.getElementById('settingsSubmenu').classList.toggle('open');
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light'); // Запоминаем
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.innerText = isDark ? '☀️' : '🌙';
    }
}
