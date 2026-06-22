const API_BASE_URL = '/api';
let currentPage = 1;
let currentFilters = {
    category: '',
    manufacturer: '',
    search: ''
};

function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
    }
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function showSpinner(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="spinner-container">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;
    }
}

async function fetchProducts(filters = {}) {
    try {
        const params = new URLSearchParams();
        if (filters.category) params.append('category', filters.category);
        if (filters.manufacturer) params.append('manufacturer', filters.manufacturer);
        if (filters.search) params.append('search', filters.search);
        
        const response = await fetch(`${API_BASE_URL}/products/?${params}`);
        if (!response.ok) throw new Error('Ошибка при загрузке товаров');
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при загрузке товаров', 'danger');
        return [];
    }
}

async function fetchProduct(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}/`);
        if (!response.ok) throw new Error('Ошибка при загрузке товара');
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при загрузке товара', 'danger');
        return null;
    }
}

async function fetchCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/categories/`);
        if (!response.ok) throw new Error('Ошибка при загрузке категорий');
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
        return [];
    }
}

async function fetchManufacturers() {
    try {
        const response = await fetch(`${API_BASE_URL}/manufacturers/`);
        if (!response.ok) throw new Error('Ошибка при загрузке производителей');
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
        return [];
    }
}

async function addToCart(productId) {
    try {
        const response = await fetch(`/cart/add/${productId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        if (response.ok) {
            showNotification('✓ Товар добавлен в корзину!', 'success');
            updateCartCount();
        } else {
            showNotification('Ошибка при добавлении товара', 'danger');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при добавлении товара', 'danger');
    }
}

async function getCartCount() {
    try {
        const response = await fetch(`${API_BASE_URL}/carts/`);
        if (response.ok) {
            const data = await response.json();
            if (data.results && data.results.length > 0) {
                const cart = data.results[0];
                let count = 0;
                for (const item of cart.товары) {
                    count += item.количество;
                }
                return count;
            }
        }
    } catch (error) {
        console.error('Ошибка при получении корзины:', error);
    }
    return 0;
}

async function updateCartCount() {
    const count = await getCartCount();
    const cartBadge = document.getElementById('cart-count');
    if (cartBadge) {
        cartBadge.textContent = count;
        cartBadge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

function renderProductCard(product) {
    const imageUrl = product.фото_товара || '/static/images/no-image.png';
    const availability = product.количество_на_складе > 0 ? 'available' : 'out-of-stock';
    const buttonDisabled = product.количество_на_складе === 0 ? 'disabled' : '';
    
    return `
        <div class="col-sm-6 col-md-4 col-lg-3 mb-4">
            <div class="card product-card h-100">
                <img src="${imageUrl}" class="card-img-top" alt="${product.название}" onerror="this.src='/static/images/no-image.png'">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${product.название}</h5>
                    <p class="card-text text-muted">${product.описание.substring(0, 100)}...</p>
                    <div class="mt-auto">
                        <div class="product-price">${product.цена} BYN</div>
                        <p class="text-muted small">
                            <i class="fas fa-cube"></i> На складе: ${product.количество_на_складе} шт.
                        </p>
                        <div class="btn-group w-100" role="group">
                            <a href="/catalog/${product.id}/" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-info-circle"></i> Подробнее
                            </a>
                            <button class="btn btn-primary btn-sm" onclick="addToCart(${product.id})" ${buttonDisabled}>
                                <i class="fas fa-shopping-cart"></i> В корзину
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderProductList(products, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (products.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <p>К сожалению, товары не найдены</p>
                </div>
            </div>
        `;
        return;
    }
    
    const html = products.map(product => renderProductCard(product)).join('');
    container.innerHTML = html;
}

async function applyFilters(category = '', manufacturer = '', search = '') {
    const containerId = 'products-container';
    showSpinner(containerId);
    
    currentFilters = { category, manufacturer, search };
    
    const filters = {};
    if (category) filters.category = category;
    if (manufacturer) filters.manufacturer = manufacturer;
    if (search) filters.search = search;
    
    const products = await fetchProducts(filters);
    renderProductList(products, containerId);
}

async function resetFilters() {
    const categorySelect = document.getElementById('category-filter');
    const manufacturerSelect = document.getElementById('manufacturer-filter');
    const searchInput = document.getElementById('search-filter');
    
    if (categorySelect) categorySelect.value = '';
    if (manufacturerSelect) manufacturerSelect.value = '';
    if (searchInput) searchInput.value = '';
    
    await applyFilters('', '', '');
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Инициализация приложения...');
    
    if (document.querySelector('[data-page="catalog"]') || document.querySelector('[data-page="home"]')) {
        updateCartCount();
    }
    
    if (document.getElementById('products-container')) {
        await applyFilters('', '', '');
    }
    
    initializeFilters();
});

function initializeFilters() {
    const categorySelect = document.getElementById('category-filter');
    const manufacturerSelect = document.getElementById('manufacturer-filter');
    const searchInput = document.getElementById('search-filter');
    const searchBtn = document.getElementById('search-btn');
    const resetBtn = document.getElementById('reset-filters-btn');
    
    if (categorySelect) {
        categorySelect.addEventListener('change', async () => {
            await applyFilters(
                categorySelect.value,
                manufacturerSelect?.value || '',
                searchInput?.value || ''
            );
        });
    }
    
    if (manufacturerSelect) {
        manufacturerSelect.addEventListener('change', async () => {
            await applyFilters(
                categorySelect?.value || '',
                manufacturerSelect.value,
                searchInput?.value || ''
            );
        });
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', async () => {
            await applyFilters(
                categorySelect?.value || '',
                manufacturerSelect?.value || '',
                searchInput.value
            );
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                await applyFilters(
                    categorySelect?.value || '',
                    manufacturerSelect?.value || '',
                    searchInput.value
                );
            }
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'BYN'
    }).format(price);
}

function truncateText(text, length) {
    if (text.length > length) {
        return text.substring(0, length) + '...';
    }
    return text;
}

console.log('main.js загружен успешно');