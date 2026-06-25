from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    """Форма для оформления заказа"""
    
    class Meta:
        model = Order
        fields = ['адрес_доставки', 'телефон']
        widgets = {
            'адрес_доставки': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите адрес доставки',
                'rows': 4
            }),
            'телефон': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите номер телефона',
                'type': 'tel'
            }),
        }