import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from manager import models
from django.utils import timezone
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import json
import datetime
from dateutil.relativedelta import relativedelta

from paypalrestsdk.notifications import WebhookEvent
from manager.payments import paypal
import paypalrestsdk
import logging

logger = logging.getLogger(__name__)

myapi = paypalrestsdk.Api({
    "mode": paypal.mode(),  # noqa
    "client_id": os.environ.get("PAYPAL_CLIENT_ID"),
    "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET")
})

# Create your views here.
class HomePageView(View):
    template_name = "userDashboard.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("app_auth:login"))

        if request.COOKIES.get('user_type', None):
            return redirect(reverse("app_auth:login_complete", kwargs={'source': 'extension'}))
        else:
            context_data = {
                "packages": models.Package.objects.all().order_by("-id"),
                "subscriptions": models.Subscription.objects.filter(
                    user=request.user.id
                ).order_by("-id"),
            }

            return render(request, self.template_name, context=context_data)


class PackageDetailView(View):
    template_name = "package.html"

    def get(self, request, slug):
        if not request.user.is_authenticated:
            response = redirect(reverse("app_auth:login"))
            response.set_cookie('next', 'manager:package')
            response.set_cookie('next_args', slug)

            return response

        package = models.Package.objects.filter(slug=slug).first()

        context_data = {
            "package": package,
            "pricings": models.Pricing.objects.filter(package=package),
            "features": models.Feature.objects.filter(package=package),
            "subscriptions": models.Subscription.objects.filter(
                user=request.user.id
            ).order_by("-id"),
            "user_package": models.Subscription.objects.filter(
                user=request.user.id, package_id = package
            ).first()
        }

        return render(request, self.template_name, context=context_data)

def SubscriptionDeactivateView(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        package = models.Package.objects.filter(slug=slug).first()
        subscription = models.Subscription.objects.filter(user=request.user.id, package_id=package).first()

        # deactivate via paypal
        ret = myapi.post(f"v1/billing/subscriptions/{subscription.order_key}/cancel")

        if ret.get("error"):
            messages.add_message(request, messages.ERROR, 'An Error occured. Please try again.')
            return redirect(reverse('manager:package', args=[models.Package.objects.filter(id=package.id).first().slug]))

        subscription.pricing=models.Pricing.objects.filter(name="Free").first()
        subscription.expiry_date=timezone.now()
        subscription.total_amount_paid=0
        subscription.order_key="Not Set"
        subscription.save()
        return redirect(reverse('manager:dashboard'))

class PaymentView(View):
    template_name = "payment.html"

    def get(self, *args, **kwargs):
        return redirect(reverse("manager:dashboard"))

    def post(self, request, *args, **kwargs):

        package_id = request.POST.get("package_id", "")
        pricing_id = request.POST.get("pricing_id", "")
        payment_duration = request.POST.get("payment_duration", "")


        # calculate total price
        price_obj = models.Pricing.objects.filter(id=pricing_id).first()
        total_price = total_price = price_obj.annualy_price if payment_duration == "annually" else int(price_obj.price)

        # detect upgrade
        # if request.GET.get('upgrade', None):
        #     # current_subscription = models.Subscription.objects.filter(user=request.user.id, package_id=package_id).first()
        #     total_price = float(price_obj.annualy_price)

        # if total_price < 0:
        #     messages.add_message(request, messages.ERROR, 'Opps! Different durations selected. Please deactivate current subscription and try again.')
        #     return redirect(reverse('manager:package', args=[models.Package.objects.filter(id=package_id).first().slug]))

        context_data = {
            "package": models.Package.objects.filter(pk=package_id).first(),
            "total_price": total_price,
            "subscription_duration": payment_duration,
            "pricing": price_obj,
        }

        return render(request, self.template_name, context=context_data)


class CompletePaymentView(View):
    def post(self, request, *args, **kwargs):

        package_id = request.POST.get("package_id", "")
        pricing_id = request.POST.get("pricing_id", "")
        total_price = request.POST.get("total_price", "")
        payment_duration = request.POST.get("payment_duration", "")

        package = models.Package.objects.filter(pk=package_id).first()
        pricing = models.Pricing.objects.filter(pk=pricing_id).first()


        # every user has a free subscription, update that  
        subscription = models.Subscription.objects.filter(user=request.user.id, package_id=package_id).first()
        if subscription.pricing.name.lower() != "Free".lower():            
            ret = myapi.post(f"v1/billing/subscriptions/{subscription.order_key}/cancel")
            if ret.get("error"):
                messages.add_message(request, messages.ERROR, 'An Error occured. Please try again.')
                return redirect(reverse('manager:package', args=[models.Package.objects.filter(id=package.id).first().slug]))

        if pricing.name.lower() == "Starter".lower():
            if payment_duration.lower() == "monthly":
                plan_id = os.environ.get("STARTER_MONTHLY")
            elif payment_duration.lower() == "annually":
                plan_id = os.environ.get("STARTER_ANNUAL")
        elif pricing.name.lower() == "Master".lower()   :
            if payment_duration.lower() == "monthly":
                plan_id = os.environ.get("MASTER_MONTHLY")
            elif payment_duration.lower() == "annually":
                plan_id = os.environ.get("MASTER_ANNUAL")
                
        data = {
            "plan_id": plan_id
        }

        ret = myapi.post("v1/billing/subscriptions", data)
        print(ret.get("error"))
        if ret.get("error"):
            messages.add_message(request, messages.ERROR, 'An Error occured. Please try again.')
            return redirect(reverse('manager:package', args=[models.Package.objects.filter(id=package.id).first().slug]))

        if ret['status'] == 'APPROVAL_PENDING':
            user = request.user
          
            subscription.pricing=models.Pricing.objects.filter(id=pricing_id).first()
            subscription.total_amount_paid=float(total_price)
            subscription.start_date=timezone.now()
            subscription.order_key=ret['id']

            subscription.save()

            redirect_url = paypal.get_url_from(ret['links'], 'approve')
            return HttpResponseRedirect(redirect_url)

@require_POST
@csrf_exempt
def paypal_webhooks(request):
    transmission_id = request.headers['Paypal-Transmission-Id']
    timestamp = request.headers['Paypal-Transmission-Time']
    webhook_id = os.environ.get("PAYPAL_WEBHOOK_ID")
    event_body = request.body.decode('utf-8')
    cert_url = request.headers['Paypal-Cert-Url']
    auth_algo = request.headers['Paypal-Auth-Algo']
    actual_signature = request.headers['Paypal-Transmission-Sig']

    response = WebhookEvent.verify(
        transmission_id,
        timestamp,
        webhook_id,
        event_body,
        cert_url,
        actual_signature,
        auth_algo
    )

    if response:
        obj = json.loads(request.body)

        event_type = obj.get('event_type')
        resource = obj.get('resource')

        if event_type == 'PAYMENT.SALE.COMPLETED':
            paypal.set_paid_until(resource, paypal.SUBSCRIPTION)

    return HttpResponse(status=200)



@login_required
def Profile(request):
    context_data = {
        'user': request.user,
        "subscriptions": models.Subscription.objects.filter(
            user=request.user.id
        ).order_by("-id")
    }
    return render(request, template_name='profile.html', context=context_data)