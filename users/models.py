from django.db import models
from django.utils import timezone

class User(models.Model):
    telegram_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='ТГ ID')
    first_name = models.CharField(max_length=200, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name='Имя пользователя')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    auth_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата авторизации')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.telegram_id}{self.first_name}{self.last_name}{self.address} {self.username} ({self.phone_number})"

class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина пользователя {self.user.first_name}"

class Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, verbose_name='Корзина')
    order_date = models.DateTimeField(default=timezone.now, verbose_name='Дата заказа')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    status = models.CharField(max_length=20, default='Создан', verbose_name='Статус')
    total_amount = models.IntegerField(verbose_name='Сумма заказа')
    product_description = models.TextField(verbose_name='Состав заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ №{self.pk} от {self.order_date}"


class BasketProduct(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, verbose_name='Корзина')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='Продукт') # Обратите внимание на products.Product
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name='Количество')
    class Meta:
        verbose_name = 'Продукт в корзине'
        verbose_name_plural = 'Продукты в корзине'

    def __str__(self):
        return f"{self.quantity} x {self.product.name} 's cart"
