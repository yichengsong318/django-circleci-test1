# Generated by Django 3.0.3 on 2020-09-02 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20200901_1058'),
        ('products', '0025_auto_20200901_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='thumbnail_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.UploadedImage'),
        ),
    ]
