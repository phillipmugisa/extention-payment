from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
import os
import uuid


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s-%s.%s" % (instance.slug ,uuid.uuid4(), ext)
    return os.path.join('images/', filename)

class Package(models.Model):
    name = models.CharField(
        _("Package Name"),
        max_length=256,
        blank=False,
        null=False
    )
    description = models.TextField(
        _("Package Description"),
        blank=False,
        null=False
    )
    slug = models.SlugField(
        _("Safe Url"),
        unique=True,
        blank = True,
        null = True,
    )
    img_url = models.ImageField(
        verbose_name=_('Package Image'),
        upload_to=get_file_path
    )

    added_on = models.DateTimeField(
        _("Upload On"),
        default=timezone.now,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        self.name = self.name.title()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name}'

class Pricing(models.Model):

    name_choices = (
        ('Basic', 'Basic'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    )

    name = models.CharField(
        _("Name"),
        max_length=256,
        blank=False,
        null=False,
        choices=name_choices
    )
    price = models.IntegerField(
        _('Pricing'),
        blank=False,
        null=False
    )
    package = models.ForeignKey(
        to=Package,
        on_delete=models.CASCADE,
        related_name='package'
    )
    def __str__(self) -> str:
        return f'{self.name}'

class Feature(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=256,
        blank=False,
        null=False
    )
    pricing = models.ManyToManyField(
        to=Pricing,
        related_name='pricing_feature'
    )
    package = models.ForeignKey(
        to=Package,
        on_delete=models.CASCADE,
        related_name='pricion_package'
    )
    def __str__(self) -> str:
        return f'{self.name}'


class Subscription(models.Model):
    user_id = models.IntegerField(
        _("User id")
    )
    package_id = models.IntegerField(
        _("Package id")
    )
    total_amount_paid =  models.IntegerField(
        _("Total Amount Paid")
    )
    start_date = models.DateField(
        _("Subscription Start Date")
    )
    expiry_date = models.DateField(
        _("Subscription Expiry Date")
    )
    email = models.CharField(
        _("Client's Email"),
        max_length=256
    )
    country_code = models.CharField(
        _("Client's Country"),
        max_length=9
    )
    address = models.CharField(
        _("Client's Address"),
        max_length=256
    )
    order_key = models.CharField(
        _("Order key"),
        max_length=256
    )