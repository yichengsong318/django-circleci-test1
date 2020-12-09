# Generated by Django 3.0.3 on 2020-08-02 18:22

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_auto_20200729_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='page',
            name='schema_draft',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        ),
    ]
