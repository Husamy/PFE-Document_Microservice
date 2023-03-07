# Generated by Django 4.1.7 on 2023-03-06 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('privacy', models.CharField(max_length=7)),
                ('type', models.CharField(max_length=3)),
                ('file', models.FileField(upload_to='documents/')),
            ],
        ),
    ]