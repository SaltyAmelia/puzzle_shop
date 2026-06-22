from rest_framework import serializers
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem

# Сериализатор для Категории
class CategorySerializer(serializers.ModelSerializer):
    """Преобразует модель Category в JSON"""
    
    class Meta:
        model = Category
        fields = ['id', 'название', 'описание']


# Сериализатор для Производителя
class ManufacturerSerializer(serializers.ModelSerializer):
    """Преобразует модель Manufacturer в JSON"""
    
    class Meta:
        model = Manufacturer
        fields = ['id', 'название', 'страна', 'описание']


# Сериализатор для Товара
class ProductSerializer(serializers.ModelSerializer):
    """Преобразует модель Product в JSON"""
    
    # Вложенные сериализаторы - показываем полные данные категории и производителя
    категория = CategorySerializer(read_only=True)
    производитель = ManufacturerSerializer(read_only=True)
    
    # ID для связей при создании/обновлении
    категория_id = serializers.IntegerField(write_only=True)
    производитель_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'название', 'описание', 'цена', 
            'количество_на_складе', 'категория', 'производитель',
            'категория_id', 'производитель_id'
        ]
    
    def create(self, validated_data):
        """Создание товара"""
        категория_id = validated_data.pop('категория_id')
        производитель_id = validated_data.pop('производитель_id')
        
        product = Product.objects.create(
            категория_id=категория_id,
            производитель_id=производитель_id,
            **validated_data
        )
        return product
    
    def update(self, instance, validated_data):
        """Обновление товара"""
        категория_id = validated_data.pop('категория_id', None)
        производитель_id = validated_data.pop('производитель_id', None)
        
        if категория_id:
            instance.категория_id = категория_id
        if производитель_id:
            instance.производитель_id = производитель_id
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


# Сериализатор для Элемента корзины
class CartItemSerializer(serializers.ModelSerializer):
    """Преобразует модель CartItem в JSON"""
    
    товар = ProductSerializer(read_only=True)
    товар_id = serializers.IntegerField(write_only=True)
    стоимость = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'товар', 'товар_id', 'количество', 'стоимость']
    
    def get_стоимость(self, obj):
        """Вычисляет стоимость элемента"""
        return float(obj.стоимость_элемента())


# Сериализатор для Корзины
class CartSerializer(serializers.ModelSerializer):
    """Преобразует модель Cart в JSON"""
    
    товары = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    общая_стоимость = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'пользователь', 'дата_создания', 'товары', 'общая_стоимость']
        read_only_fields = ['пользователь', 'дата_создания']
    
    def get_общая_стоимость(self, obj):
        """Вычисляет общую стоимость корзины"""
        return float(obj.общая_стоимость())


# Сериализатор для Элемента заказа
class OrderItemSerializer(serializers.ModelSerializer):
    """Преобразует модель OrderItem в JSON"""
    
    товар = ProductSerializer(read_only=True)
    стоимость = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'товар', 'количество', 'цена', 'стоимость']
    
    def get_стоимость(self, obj):
        """Вычисляет стоимость позиции"""
        return float(obj.стоимость_позиции())


# Сериализатор для Заказа
class OrderSerializer(serializers.ModelSerializer):
    """Преобразует модель Order в JSON"""
    
    товары = OrderItemSerializer(source='товары', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'пользователь', 'адрес_доставки', 'телефон',
            'дата_заказа', 'статус', 'общая_стоимость', 'товары'
        ]
        read_only_fields = ['пользователь', 'дата_заказа', 'общая_стоимость']