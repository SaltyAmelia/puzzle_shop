// Получить токен из localStorage
function getAccessToken() {
    return localStorage.getItem('access_token');
}

// Сохранить токены
function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

// Удалить токены (выход)
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// Регистрация
async function register(username, email, password, passwordConfirm, firstName, lastName) {
    try {
        const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password,
                password_confirm: passwordConfirm,
                first_name: firstName,
                last_name: lastName
            })
        });

        if (response.ok) {
            showNotification('Регистрация успешна! Теперь войдите.', 'success');
            return true;
        } else {
            const data = await response.json();
            showNotification(JSON.stringify(data), 'danger');
            return false;
        }
    } catch (error) {
        console.error('Ошибка регистрации:', error);
        showNotification('Ошибка при регистрации', 'danger');
        return false;
    }
}

// Вход
async function login(username, password) {
    try {
        const response = await fetch('/api/auth/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            saveTokens(data.access, data.refresh);
            showNotification('Успешный вход!', 'success');
            setTimeout(() => window.location.href = '/profile/', 1000);
            return true;
        } else {
            showNotification('Неправильное имя или пароль', 'danger');
            return false;
        }
    } catch (error) {
        console.error('Ошибка входа:', error);
        showNotification('Ошибка при входе', 'danger');
        return false;
    }
}

// Выход
function logout() {
    clearTokens();
    showNotification('Вы вышли из системы', 'info');
    window.location.href = '/';
}

// Получить профиль
async function getProfile() {
    try {
        const token = getAccessToken();
        if (!token) {
            return null;
        }

        const response = await fetch('/api/me/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            return await response.json();
        } else if (response.status === 401) {
            clearTokens();
            return null;
        }
    } catch (error) {
        console.error('Ошибка получения профиля:', error);
        return null;
    }
}

// Обновить профиль
async function updateProfile(data) {
    try {
        const token = getAccessToken();
        if (!token) {
            showNotification('Необходимо войти в систему', 'warning');
            return false;
        }

        const response = await fetch('/api/me/', {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showNotification('Профиль обновлен!', 'success');
            return true;
        } else if (response.status === 401) {
            clearTokens();
            showNotification('Сессия истекла. Войдите снова.', 'warning');
            return false;
        } else {
            const errorData = await response.json();
            showNotification(JSON.stringify(errorData), 'danger');
            return false;
        }
    } catch (error) {
        console.error('Ошибка обновления профиля:', error);
        showNotification('Ошибка при обновлении профиля', 'danger');
        return false;
    }
}

// Проверить авторизацию
async function checkAuth() {
    const profile = await getProfile();
    const authBtn = document.getElementById('auth-button');
    const profileBtn = document.getElementById('profile-button');
    
    if (profile) {
        if (authBtn) authBtn.style.display = 'none';
        if (profileBtn) profileBtn.style.display = 'block';
        return true;
    } else {
        if (authBtn) authBtn.style.display = 'block';
        if (profileBtn) profileBtn.style.display = 'none';
        return false;
    }
}

// При загрузке страницы
document.addEventListener('DOMContentLoaded', checkAuth);