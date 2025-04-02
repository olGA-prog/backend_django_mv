from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .models import User, Basket, Order, BasketProduct
from .serializers import UserSerializer, BasketSerializer, OrderSerializer, BasketProductSerializer
import os
from yookassa import Configuration, Payment
from django.conf import settings
from backend_django_mv.authMiddle import JWTAuthentication
from products.models import Product
from django.utils import timezone

Configuration.account_id = os.environ.get('YOO_KASSA_SHOP_ID')
Configuration.secret_key = os.environ.get('YOO_KASSA_SECRET_KEY')


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [JWTAuthentication]

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [JWTAuthentication]

# Представления для Order
class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [JWTAuthentication]

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [JWTAuthentication]




# Представления для BasketProduct
class BasketProductList(generics.ListCreateAPIView):
    serializer_class = BasketProductSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        return BasketProduct.objects.filter(basket=self.request.user.basket)

    def perform_create(self, serializer):
        serializer.save(basket=self.request.user.basket)

class BasketProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BasketProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BasketProduct.objects.filter(basket=self.request.user.basket)

class BasketList(generics.ListCreateAPIView):
    serializer_class = BasketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            return Basket.objects.filter(user=self.request.user)
        except Basket.DoesNotExist:
            return Basket.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BasketDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BasketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user)

@csrf_exempt
@permission_classes([JWTAuthentication])
def create_payment(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        if not address:
            return JsonResponse({'message': 'Необходимо указать адрес доставки.'}, status=400)
        try:
            payment = Payment.create({
                "amount": {
                    "value": "100.00",  # Сумма заказа
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://localhost:3000/success"  # Замените на ваш URL успешной оплаты
                },
                "capture": True,
                "description": "Заказ номер 123"  # Описание заказа
            })
            payment_url = payment.confirmation.confirmation_url
            return JsonResponse({'payment_url': payment_url})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Недопустимый метод.'}, status=405)



@api_view(['GET'])
@permission_classes([JWTAuthentication])
def add_to_basket(request):
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity')
    user_id = request.GET.get('user_id')


    if not all([product_id, quantity, user_id]):
        return Response({'message': 'Не все параметры переданы'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(pk=product_id)

    except Product.DoesNotExist:

        return Response({'message': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

    try:
        basket = Basket.objects.get(user=user_id)

    except Basket.DoesNotExist:
        return Response({'message': 'Корзина не найдена для данного пользователя'}, status=status.HTTP_404_NOT_FOUND)

    try:
        basket_product, created = BasketProduct.objects.get_or_create(
            basket=basket,
            product=product
        )
        if created:
            basket_product.quantity = Decimal(quantity)
            basket_product.save()
        else:
            basket_product.quantity += Decimal(quantity)

        basket_product.save()
        serializer = BasketProductSerializer(basket_product)
        return Response(serializer.data,  status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([JWTAuthentication])
def get_basket_items(request):
    user_id = request.GET.get('user_id')
    try:
        basket = Basket.objects.get(user=user_id)
    except Basket.DoesNotExist:
        return Response({'message': 'Корзина не найдена'}, status=status.HTTP_404_NOT_FOUND)
    try:
        basket_products = BasketProduct.objects.filter(basket=basket)

        serializer = BasketProductSerializer(basket_products, many=True)

        return Response(serializer.data, status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([JWTAuthentication])
def remove_from_basket(request,  user_id, item_id):
    try:
        basket = Basket.objects.get(user=user_id)

    except Basket.DoesNotExist:

        return Response({'message': 'Корзина не найдена для данного пользователя'}, status=status.HTTP_404_NOT_FOUND)

    try:
        basket_product = BasketProduct.objects.get(pk=item_id,basket=basket)

        basket_product.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    except BasketProduct.DoesNotExist:

        return Response({'message': 'Продукт в корзине не найден'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([JWTAuthentication])
def update_basket_item(request, user_id, item_id):
    try:
        quantity_str = request.data.get('quantity')
        if not quantity_str:
            return Response({'message': 'Не передано новое значение quantity'}, status=status.HTTP_400_BAD_REQUEST)

        quantity = Decimal(quantity_str)
    except (ValueError, TypeError):
        return Response({'message': 'Некорректное значение quantity'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        basket = Basket.objects.get(user=user_id)
    except Basket.DoesNotExist:
        return Response({'message': 'Корзина не найдена для данного пользователя'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Получаем BasketProduct для данной корзины и item_id
        basket_product = BasketProduct.objects.get(basket=basket, pk=item_id)
    except BasketProduct.DoesNotExist:
        return Response({'message': 'Товар в корзине не найден'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Обновляем количество
        basket_product.quantity = quantity
        basket_product.save()

        return Response({'message': 'Количество товара в корзине обновлено'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([JWTAuthentication])
def create_order(request):
    user_id = request.data.get('user_id')
    total_amount = request.data.get('total_amount')
    address = request.data.get('address')
    name = request.data.get('name')
    phone = request.data.get('phone')


    if not all([user_id, total_amount, address, name, phone]):
        return Response({'message': 'Не все обязательные поля заполнены'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=user_id)
        user.name = name
        user.save()
        user.phone_number = phone
        user.save()
        basket = Basket.objects.get(user=user)  # Use user instead of user_id
    except User.DoesNotExist:
        return Response({'message': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    try:
        total_amount = Decimal(total_amount)
    except (ValueError, TypeError):
        return Response({'message': 'Некорректное значение total_amount'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        basket_products = BasketProduct.objects.filter(basket=basket)
        product_description = ""

        for basket_product in basket_products:
            product_name = basket_product.product.name
            product_price = basket_product.product.price
            quantity = basket_product.quantity
            product_description += f"{product_name} - цена за кг. - {product_price} руб. - количество: {quantity} кг.\n"
        print(product_description)
        order = Order.objects.create(
            basket=basket,
            user=user,
            total_amount=total_amount,
            status='Создан',
            order_date=timezone.now(),
            product_description=product_description
        )
        BasketProduct.objects.filter(basket=basket).delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    except ObjectDoesNotExist as e:
        print(f"Объект не найден: {str(e)}")
        return Response({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Общая ошибка: {str(e)}")
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    finally:
        print("Завершение обработки заказа")
