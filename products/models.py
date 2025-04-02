from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название категории')
    description = models.TextField(default='Нет описания категории', verbose_name='Описание')
    img = models.CharField(max_length=255, default='defaultImg_Category', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Type(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название типа')
    unit = models.CharField(max_length=100, null=True, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Тип'
        verbose_name_plural = 'Типы'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    price = models.IntegerField(verbose_name='Цена')
    description = models.TextField(verbose_name='Описание')
    count = models.IntegerField(verbose_name='Количество')
    img = models.CharField(max_length=255, default='defaultImg', verbose_name='Изображение')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='Тип')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name
