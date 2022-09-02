from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
import os
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from app_auth.models import User


def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s-%s.%s" % (instance.slug, uuid.uuid4(), ext)
    return os.path.join("images/", filename)


class Package(models.Model):
    name = models.CharField(_("Package Name"), max_length=256, blank=False, null=False)
    description = models.TextField(_("Package Description"), blank=False, null=False)
    slug = models.SlugField(
        _("Safe Url"),
        unique=True,
        blank=True,
        null=True,
    )
    img_url = models.ImageField(
        verbose_name=_("Package Image"), upload_to=get_file_path
    )

    added_on = models.DateTimeField(
        _("Upload On"),
        default=timezone.now,
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)

        self.name = self.name.title()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"


class Pricing(models.Model):

    name = models.CharField(_("Name"), max_length=256, blank=False, null=False)
    price = models.IntegerField(_("Monthly Pricing"), blank=False, null=False)
    package = models.ForeignKey(
        to=Package, on_delete=models.CASCADE, related_name="package"
    )
    annualy_price = models.IntegerField(_("Annual Pricing"), blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Feature(models.Model):
    name = models.CharField(_("Name"), max_length=256, blank=False, null=False)
    pricing = models.ManyToManyField(to=Pricing, related_name="pricing_feature")
    package = models.ForeignKey(
        to=Package, on_delete=models.CASCADE, related_name="pricion_package"
    )

    def __str__(self) -> str:
        return f"{self.name}"


class Subscription(models.Model):
    user = models.IntegerField(_("User id"))
    user_type = models.CharField(_("User Type"), max_length=20, default="User")
    package_id = models.ForeignKey(to=Package, on_delete=models.CASCADE)
    pricing = models.ForeignKey(to=Pricing, on_delete=models.CASCADE)
    total_amount_paid = models.DecimalField(
        _("Total Amount Paid"), decimal_places=2, max_digits=8
    )
    start_date = models.DateField(_("Subscription Start Date"), default=timezone.now)
    expiry_date = models.DateField(_("Subscription Expiry Date"))
    email = models.CharField(_("Client's Email"), max_length=256)
    country_code = models.CharField(_("Client's Country"), max_length=9)
    address = models.CharField(_("Client's Address"), max_length=256)
    order_key = models.CharField(_("Order key"), max_length=256)
    expired = models.BooleanField(_("Expired"), default=False)
    active = models.BooleanField(_("Active"), default=True)


    def __str__(self) -> str:
        return User.objects.filter(id=self.user).first().username


@receiver(post_save, sender=Pricing)
def set_pricing(sender, instance, *args, **kwargs):
    if not instance.annualy_price and instance.annualy_price != 0:
        instance.annualy_price = int(instance.price * 12)
        instance.save()

@receiver(post_save, sender=User)
def set_dafault_package(sender, instance, *args, **kwargs):
    if not Subscription.objects.filter(user = instance.pk):
        # create subsription
        subcription = Subscription(
            user=instance.id,
            user_type=instance.__class__.__name__,
            package_id=Package.objects.all().first(),
            pricing=Pricing.objects.filter(name="Free").first(),
            expiry_date=timezone.now(),
            total_amount_paid=0,
            email=instance.email,
            address="Not Set",
            country_code="Not Set",
            order_key="Not Set",
        )
        subcription.save()