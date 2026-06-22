from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

#  REST API ROUTER 
router = DefaultRouter()
router.register(r'api/categories', views.CategoryViewSet, basename='category')
router.register(r'api/manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'api/products', views.ProductViewSet, basename='product')
router.register(r'api/carts', views.CartViewSet, basename='cart')
router.register(r'api/cart-items', views.CartItemViewSet, basename='cart-item')
router.register(r'api/orders', views.OrderViewSet, basename='order')
router.register(r'api/order-items', views.OrderItemViewSet, basename='order-item')

#  WEB МАРШРУТЫ 
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('author/', views.author, name='author'),
    
    # Каталог
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Корзина
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Заказ
    path('checkout/', views.checkout, name='checkout'),
    
    # REST API URLs
    path('', include(router.urls)),
]