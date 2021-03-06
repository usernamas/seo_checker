# Generated by Django 2.0.3 on 2018-04-02 16:49

import checkup.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.CharField(max_length=200)),
                ('score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2000, validators=[checkup.validators.validate_url])),
                ('check_date', models.DateTimeField(verbose_name='date checked')),
            ],
        ),
        migrations.AddField(
            model_name='result',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkup.Website'),
        ),
    ]
