# Generated by Django 3.0.3 on 2020-06-14 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20200614_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contentitem',
            name='cloudflare_video',
        ),
        migrations.AddField(
            model_name='contentitem',
            name='media_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.DeleteModel(
            name='CloudflareVideo',
        ),
    ]
