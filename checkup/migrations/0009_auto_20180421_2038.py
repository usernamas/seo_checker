# Generated by Django 2.0.3 on 2018-04-21 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checkup', '0008_auto_20180421_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rule_name', to='checkup.Rule'),
        ),
    ]
