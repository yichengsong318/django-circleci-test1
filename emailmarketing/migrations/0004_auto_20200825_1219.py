# Generated by Django 3.0.3 on 2020-08-25 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_uploadedvideo'),
        ('emailmarketing', '0003_emailsubscriber'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='emailsubscriber',
            unique_together={('store', 'email')},
        ),
    ]
