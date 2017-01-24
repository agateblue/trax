# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-24 19:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingWebhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('token', models.CharField(db_index=True, max_length=100, unique=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_integrations.incomingwebhook_set+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]