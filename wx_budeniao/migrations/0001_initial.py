# Generated by Django 4.0.6 on 2022-07-16 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=32)),
                ('alipay', models.CharField(max_length=32)),
                ('orders', models.IntegerField()),
            ],
        ),
    ]
