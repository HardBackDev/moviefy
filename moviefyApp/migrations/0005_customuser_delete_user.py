# Generated by Django 4.2.10 on 2024-02-26 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviefyApp', '0004_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=255, unique=True)),
                ('password', models.CharField(max_length=1000)),
                ('role', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]