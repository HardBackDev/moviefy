# Generated by Django 4.2.10 on 2024-02-27 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviefyApp', '0005_customuser_delete_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]