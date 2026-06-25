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
        from rest_framework import serializers
from django.contrib.auth.models import User
from shop.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 'city', 'favorite_category', 'is_admin']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            user.email = user_data.get('email', user.email)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Profile.objects.create(user=user)
        return user