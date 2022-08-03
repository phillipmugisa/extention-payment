# Generated by Django 4.0.6 on 2022-07-20 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("manager", "0002_alter_pricing_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="package",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pricion_package",
                to="manager.package",
            ),
            preserve_default=False,
        ),
    ]
