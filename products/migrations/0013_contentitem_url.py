# Generated by Django 3.0.3 on 2020-06-15 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20200614_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentitem',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
