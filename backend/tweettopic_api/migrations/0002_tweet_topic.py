# Generated by Django 3.0.3 on 2020-03-17 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweettopic_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='topic',
            field=models.TextField(default=None),
        ),
    ]
