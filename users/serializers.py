from rest_framework import serializers
from .models import User, Basket, Order, BasketProduct
from products.serializers import ProductSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['telegram_id', 'first_name', 'last_name', 'username', 'address', 'phone_number', 'auth_date']
        extra_kwargs = {'auth_date': {'required': False, 'allow_null': True}}

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class BasketProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = BasketProduct
        fields = ['id', 'product', 'quantity']

class BasketSerializer(serializers.ModelSerializer):
    basketproduct_set = BasketProductSerializer(many=True, read_only=True) #Для отображения продуктов в корзине
    class Meta:
        model = Basket
        fields = ['id', 'basketproduct_set']