from django.http import HttpResponse
from .models import Product, Category

def index(request):
    """Главная страница с ссылками"""
    return HttpResponse("""
        <h1>Магазин необычных головоломок и пазлов</h1>
        <p>Добро пожаловать в наш магазин!</p>
        <ul>
            <li><a href="/products/">Каталог товаров</a></li>
            <li><a href="/about/">О магазине</a></li>
            <li><a href="/author/">Об авторе</a></li>
        </ul>
    """)

def about(request):
    """Страница о магазине"""
    return HttpResponse("""
        <h1>О магазине</h1>
        <p><b>Тема:</b> Магазин необычных головоломок и пазлов</p>
        <p>Мы продаём головоломки и пазлы для развития логики!</p>
        <p><a href="/">Назад на главную</a></p>
    """)

def author(request):
    """Страница об авторе"""
    return HttpResponse("""
        <p><a href="/">Назад на главную</a></p>
    """)

def products_list(request):
    """Страница со списком всех товаров"""
    products = Product.objects.all()
    
    html = "<h1>Каталог товаров</h1>"
    html += "<p><a href='/'>На главную</a></p>"
    
    for product in products:
        html += f"""
        <div style='border: 1px solid #ccc; padding: 10px; margin: 10px;'>
            <h3>{product.название}</h3>
            <p>Цена: {product.цена} руб.</p>
            <p>На складе: {product.количество_на_складе} шт.</p>
            <p>Категория: {product.категория.название}</p>
            <p>Производитель: {product.производитель.название}</p>
        </div>
        """
    
    return HttpResponse(html)