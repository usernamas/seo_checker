# Generated by Django 2.0.3 on 2018-05-23 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkup', '0017_auto_20180524_0127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rule',
            name='group',
        ),
    ]
