# Generated by Django 2.0.3 on 2018-05-23 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkup', '0018_remove_rule_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='description',
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
    ]
