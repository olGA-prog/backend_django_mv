# Generated by Django 5.1.7 on 2025-03-30 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_name_user_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basketproduct',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=5, verbose_name='Количество'),
        ),
    ]
