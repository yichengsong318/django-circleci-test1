# Generated by Django 3.0.3 on 2020-06-21 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_store_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='store',
            old_name='vat_address',
            new_name='tax_address',
        ),
        migrations.AddField(
            model_name='store',
            name='collect_tax_address',
            field=models.BooleanField(default=False),
        ),
    ]
