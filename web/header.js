function renderHeader() {
    const header = document.createElement('header');
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username') || 'Користувач';

    // Спільна частина логотипу
    let navContent = `
        <nav class="top-nav">
            <a href="index.html" class="logo">MovieMatch</a>
            <ul class="nav-links">
                <li><a href="index.html#popular">Popular</a></li>
                <li><a href="index.html#about">About</a></li>
                <li><a href="index.html#contacts">Contacts</a></li>
            </ul>
    `;

    if (token) {
        // Шапка для ЗАЛОГІНЕНОГО користувача
        navContent += `
            <div class="user-menu" style="display: flex; align-items: center; gap: 15px;">
                <a href="my_films.html" style="color: white; text-decoration: none;">My Collection</a>
                <a href="profile.html" style="color: white; text-decoration: none;">Friends</a>
                <div class="user-info" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-weight: bold;">${username}</span>
                    <div class="avatar" style="width: 35px; height: 35px; background-color: var(--accent-pink); border-radius: 50%;"></div>
                </div>
                <button onclick="logout()" class="btn-alt" style="padding: 5px 15px; cursor: pointer;">Exit</button>
            </div>
        `;
    } else {
        // Шапка для НЕЗАЛОГІНЕНОГО користувача
        navContent += `
            <div class="auth-buttons" style="display: flex; gap: 10px;">
                <a href="login.html" class="btn-alt" style="text-decoration: none; padding: 8px 20px;">Log In</a>
                <a href="signup.html" class="btn-main" style="text-decoration: none; padding: 8px 20px; background: var(--accent-pink); border-radius: 20px;">Sign Up</a>
            </div>
        `;
    }

    navContent += `</nav>`;
    header.innerHTML = navContent;

    // Вставляємо на початок body
    document.body.prepend(header);
}

// Функція виходу
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Запуск при завантаженні сторінки
document.addEventListener('DOMContentLoaded', renderHeader);