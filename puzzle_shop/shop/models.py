from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Модель "Категория товара"
class Category(models.Model):
    название = models.CharField(max_length=100, verbose_name="Название категории")
    описание = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.название
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


# Модель "Производитель"
class Manufacturer(models.Model):
    название = models.CharField(max_length=100, verbose_name="Название производителя")
    страна = models.CharField(max_length=100, verbose_name="Страна")
    описание = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.название
    
    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"


# Модель "Товар"
class Product(models.Model):
    название = models.CharField(max_length=200, verbose_name="Название товара")
    описание = models.TextField(verbose_name="Описание")
    фото_товара = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото товара")
    цена = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
    количество_на_складе = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Количество на складе"
    )
    категория = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    производитель = models.ForeignKey(
        Manufacturer, 
        on_delete=models.CASCADE,
        verbose_name="Производитель"
    )
    
    def __str__(self):
        return self.название
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


# Модель "Корзина"
class Cart(models.Model):
    пользователь = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    дата_создания = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return f"Корзина пользователя {self.пользователь.username}"
    
    def общая_стоимость(self):
        """Вычисляет общую стоимость всех товаров в корзине"""
        total = 0
        for item in self.cartitem_set.all():
            total += item.стоимость_элемента()
        return total
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


# Модель "Элемент корзины"
# Модель "Элемент корзины"
class CartItem(models.Model):
    корзина = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE,
        verbose_name="Корзина"
    )
    товар = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    количество = models.PositiveIntegerField(verbose_name="Количество")
    
    def __str__(self):
        return f"{self.товар.название} ({self.количество} шт.)"
    
    def стоимость_элемента(self):
        """Вычисляет стоимость этого элемента корзины"""
        return self.товар.цена * self.количество
    
    def clean(self):
        """Проверяет, что количество не превышает количество на складе"""
        from django.core.exceptions import ValidationError
        
        # Проверяем что товар и количество установлены
        if self.товар and self.количество:
            if self.количество > self.товар.количество_на_складе:
                raise ValidationError(
                    f'Недостаточно товара на складе. Доступно: {self.товар.количество_на_складе}'
                )
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"