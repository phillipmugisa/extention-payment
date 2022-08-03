# Generated by Django 4.0.6 on 2022-07-20 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manager", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pricing",
            name="name",
            field=models.CharField(
                choices=[
                    ("Basic", "Basic"),
                    ("Gold", "Gold"),
                    ("Platinum", "Platinum"),
                ],
                max_length=256,
                verbose_name="Name",
            ),
        ),
    ]
