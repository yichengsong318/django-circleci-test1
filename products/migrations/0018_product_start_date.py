# Generated by Django 3.0.3 on 2020-07-07 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_product_free'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
