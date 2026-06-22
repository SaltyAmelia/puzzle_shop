from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Category, Manufacturer, Cart, CartItem

# Главная страница
def index(request):
    return render(request, 'shop/index.html')

# Каталог товаров
def product_list(request):
    """Список товаров с фильтрацией и поиском"""
    products = Product.objects.all()
    
    # Фильтр по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(категория_id=category_id)
    
    # Фильтр по производителю
    manufacturer_id = request.GET.get('manufacturer')
    if manufacturer_id:
        products = products.filter(производитель_id=manufacturer_id)
    
    # Поиск по названию или описанию
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(название__icontains=search_query) | 
            Q(описание__icontains=search_query)
        )
    
    # Получаем все категории и производителей для фильтров
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'search_query': search_query,
    }
    return render(request, 'shop/product_list.html', context)

# Детальная информация о товаре
def product_detail(request, pk):
    """Подробная информация о товаре"""
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'shop/product_detail.html', context)

# Добавление товара в корзину
@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем или создаём корзину для пользователя
    cart, created = Cart.objects.get_or_create(пользователь=request.user)
    
    # Проверяем есть ли товар уже в корзине
    cart_item, created = CartItem.objects.get_or_create(
        корзина=cart,
        товар=product,
        defaults={'количество': 1}
    )
    
    # Если товар уже был в корзине, увеличиваем количество
    if not created:
        if cart_item.количество < product.количество_на_складе:
            cart_item.количество += 1
            cart_item.save()
    
    return redirect('cart_view')

# Обновление количества товара в корзине
@login_required
def update_cart(request, item_id):
    """Обновление количества товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Проверяем что количество не превышает запас
        if quantity > 0 and quantity <= cart_item.товар.количество_на_складе:
            cart_item.количество = quantity
            cart_item.save()
    
    return redirect('cart_view')

# Удаление товара из корзины
@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    cart_item.delete()
    return redirect('cart_view')

# Просмотр корзины
@login_required
def cart_view(request):
    """Отображение корзины пользователя"""
    cart, created = Cart.objects.get_or_create(пользователь=request.user)
    cart_items = CartItem.objects.filter(корзина=cart)
    
    # Вычисляем общую стоимость
    total = sum(item.стоимость_элемента() for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)

# Страницы из прошлых лаб
def about(request):
    return render(request, 'shop/about.html')

def author(request):
    return render(request, 'shop/author.html')

from io import BytesIO
from openpyxl import Workbook
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from .forms import CheckoutForm
from .models import Order, OrderItem

# Оформление заказа
@login_required
def checkout(request):
    """Страница оформления заказа"""
    
    # Получаем корзину пользователя
    try:
        cart = Cart.objects.get(пользователь=request.user)
        cart_items = CartItem.objects.filter(корзина=cart)
    except Cart.DoesNotExist:
        return redirect('product_list')
    
    # Если корзина пуста, редирект
    if not cart_items.exists():
        return redirect('cart_view')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Создаём заказ
            order = form.save(commit=False)
            order.пользователь = request.user
            
            # Вычисляем общую стоимость
            total = sum(item.стоимость_элемента() for item in cart_items)
            order.общая_стоимость = total
            order.save()
            
            # Копируем товары из корзины в заказ
            for item in cart_items:
                OrderItem.objects.create(
                    заказ=order,
                    товар=item.товар,
                    количество=item.количество,
                    цена=item.товар.цена
                )
            
            # Генерируем и отправляем чек
            send_receipt(order)
            
            # Очищаем корзину
            cart_items.delete()
            
            # Показываем сообщение об успехе
            return render(request, 'shop/order_success.html', {'order': order})
    else:
        form = CheckoutForm()
    
    # Вычисляем итоговую сумму
    total = sum(item.стоимость_элемента() for item in cart_items)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)


def send_receipt(order):
    """Генерирует и отправляет чек по email"""
    
    # Создаём Excel файл
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Чек заказа"
    
    # Заголовок
    worksheet['A1'] = f"ЧЕК ЗАКАЗА №{order.id}"
    worksheet['A2'] = f"Дата: {order.дата_заказа.strftime('%d.%m.%Y %H:%M')}"
    worksheet['A3'] = f"Покупатель: {order.пользователь.username}"
    
    # Таблица товаров
    worksheet['A5'] = "Товар"
    worksheet['B5'] = "Количество"
    worksheet['C5'] = "Цена"
    worksheet['D5'] = "Сумма"
    
    row = 6
    for item in order.товары.all():
        worksheet[f'A{row}'] = item.товар.название
        worksheet[f'B{row}'] = item.количество
        worksheet[f'C{row}'] = float(item.цена)
        worksheet[f'D{row}'] = float(item.стоимость_позиции())
        row += 1
    
    # Итого
    worksheet[f'A{row + 1}'] = "ИТОГО:"
    worksheet[f'D{row + 1}'] = float(order.общая_стоимость)
    
    # Информация о доставке
    worksheet[f'A{row + 3}'] = "Адрес доставки:"
    worksheet[f'A{row + 4}'] = order.адрес_доставки
    worksheet[f'A{row + 5}'] = f"Телефон: {order.телефон}"
    
    # Сохраняем файл в памяти
    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)
    
    # Отправляем email
    subject = f"Ваш чек заказа №{order.id}"
    message = f"""
    Здравствуйте, {order.пользователь.username}!
    
    Спасибо за ваш заказ №{order.id}.
    Общая сумма: {order.общая_стоимость} руб.
    
    Адрес доставки: {order.адрес_доставки}
    Телефон: {order.телефон}
    
    Ваш чек прикреплён к этому письму.
    """
    
    # Отправляем письмо с чеком
    from django.core.mail import EmailMessage
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.пользователь.email],
    )
    
    # Прикрепляем Excel файл
    email.attach(
        f'receipt_{order.id}.xlsx',
        excel_file.getvalue(),
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    try:
        email.send()
        print(f"Чек успешно отправлен на {order.пользователь.email}")
    except Exception as e:
        print(f"Ошибка при отправке чека: {e}")