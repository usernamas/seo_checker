# Generated by Django 2.0.3 on 2018-04-21 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkup', '0009_auto_20180421_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message',
            field=models.TextField(max_length=5000),
        ),
    ]
