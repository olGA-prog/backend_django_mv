# Generated by Django 5.1.7 on 2025-03-31 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_basketproduct_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product_description',
            field=models.TextField(default='No description', verbose_name='Состав заказа'),
            preserve_default=False,
        ),
    ]
