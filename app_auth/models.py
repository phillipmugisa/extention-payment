from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

from manager.models import Subscription, Package, Pricing

class User(AbstractUser):
    def str(self):
        return self.username

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