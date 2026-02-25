function renderHeader() {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username') || 'User';
    const headerElement = document.querySelector('header');

    if (!headerElement) return;

    headerElement.innerHTML = `
        <nav class="top-nav">
            <div class="logo">
                <a href="index.html">MovieMatch</a>
            </div>
            <ul class="nav-links">
                <li><a href="index.html#popular">Popular</a></li>
                <li><a href="index.html#about">About</a></li>
                <li><a href="index.html#contacts">Contacts</a></li>
                ${token ? '<li><a href="profile.html">Friends</a></li>' : ''}
                ${token ? '<li><a href="my_films.html">My Collection</a></li>' : ''}
                ${ token ? '<li><a href="search_friends.html" ">Search Friends</a></li>' : '' }
            </ul>
            <div class="auth-lang">
                ${token ? `
                    <div class="user-profile">
                        <span class="username">${username}</span>
                        <button onclick="handleSignOut()" class="btn-signout">Sign Out</button>
                    </div>
                ` : `
                    <a href="login.html" class="btn-login">Login</a>
                `}
            </div>
        </nav>
        <nav class="sub-nav">
            <a href="index.html">Movies</a>
            <a href="development.html">Books</a>
            <a href="development.html">Cartoons</a>
            <a href="development.html">Audiobooks</a>
            <a href="development.html">Podcasts</a>
            <a href="development.html">Playlists</a>
            <a href="development.html">Show</a>
            <a href="development.html">TV shows</a>
        </nav>
    `;
}

function handleSignOut() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

document.addEventListener('DOMContentLoaded', renderHeader);




