import os
import paypalrestsdk
import logging
from datetime import datetime, timedelta
from manager import models

from django.conf import settings

logger = logging.getLogger(__name__)

BASE_DIR = os.path.join(
    "..",  # proj
    "..",  # land
    os.path.dirname(__file__)  # commands
)

PRODUCT_CONF_PATH = os.path.join("paypal", "product.yml")
PLAN_CONF_PATH = os.path.join("paypal", "plan.yml")
ORDER_CONF_PATH = os.path.join("paypal", "order.yml")

PRODUCT = "product"
PLAN = "plan"

SUBSCRIPTION = 'subscription'
ORDER = 'order'


def mode():
    if settings.DEBUG:
        return "sandbox"

    return "live"


myapi = paypalrestsdk.Api({
    "mode": mode(),  # noqa
    "client_id":  os.environ.get("PAYPAL_CLIENT_ID"),
    "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET")
})


def get_url_from(iterator, what):
    for link in iterator:
        if link['rel'] == what:
            return link['href']


def plus_days(count):
    _date = datetime.now()
    return _date + timedelta(days=count)


def set_paid_until(obj, from_what):

    if from_what == SUBSCRIPTION:
        billing_agreement_id = obj['billing_agreement_id']
        # get subscription details
        ret = myapi.get(f"v1/billing/subscriptions/{billing_agreement_id}")

        try:
            subscription = models.Subscription.objects.filter(order_key=billing_agreement_id).first()
        except:
            return False

        logger.debug(f"SUBSCRIPTION {obj}")
        

    return True
