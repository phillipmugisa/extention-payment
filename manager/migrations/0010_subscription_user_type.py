# Generated by Django 4.0.6 on 2022-08-03 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0009_rename_user_id_subscription_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='user_type',
            field=models.CharField(default='User', max_length=20, verbose_name='User Type'),
        ),
    ]