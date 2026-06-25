from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem
# Регистрация модели "Категория"
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['название', 'описание']
    search_fields = ['название']


# Регистрация модели "Производитель"
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['название', 'страна']
    search_fields = ['название', 'страна']


# Регистрация модели "Товар"
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['название', 'цена', 'количество_на_складе', 'категория', 'производитель']
    list_filter = ['категория', 'производитель']
    search_fields = ['название', 'описание']


# Inline для элементов корзины (показываем их внутри корзины)
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


# Регистрация модели "Корзина"
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['пользователь', 'дата_создания']
    inlines = [CartItemInline]


# Регистрация модели "Элемент корзины"
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['товар', 'корзина', 'количество', 'стоимость_элемента']

    # Inline для товаров в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

# Регистрация модели "Заказ"
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'пользователь', 'дата_заказа', 'статус', 'общая_стоимость']
    list_filter = ['статус', 'дата_заказа']
    search_fields = ['пользователь__username', 'адрес_доставки']
    inlines = [OrderItemInline]

# Регистрация модели "Товар в заказе"
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['заказ', 'товар', 'количество', 'цена']