from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem

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