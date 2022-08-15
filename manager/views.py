from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from manager import models
from django.utils import timezone
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import json
import datetime
from dateutil.relativedelta import relativedelta

from paypalcheckoutsdk.orders import OrdersGetRequest
from .paypal import PayPalClient

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
        if request.GET.get('upgrade', None):
            current_subscription = models.Subscription.objects.filter(user=request.user.id, package_id=package_id).first()
            total_price = float(price_obj.annualy_price) - float(current_subscription.total_amount_paid) if payment_duration == "annually" else  float(price_obj.price) - float(current_subscription.total_amount_paid)

        if total_price < 0:
            messages.add_message(request, messages.ERROR, 'Opps! Different durations selected. Please deactivate current subscription and try again.')
            return redirect(reverse('manager:package', args=[models.Package.objects.filter(id=package_id).first().slug]))

        context_data = {
            "package_id": package_id,
            "total_price": total_price,
            "subscription_duration": payment_duration,
            "pricing_id": price_obj.id,
        }

        return render(request, self.template_name, context=context_data)


class CompletePaymentView(View):
    def post(self, request, *args, **kwargs):

        PPClient = PayPalClient()

        body = json.loads(request.body)

        data = body["orderID"]
        package_id = body["package_id"]
        subscription_duration = body["subscription_duration"]
        pricing_id = body["pricing_id"]

        expiry_date = timezone.now() + datetime.timedelta(days=30)

        if subscription_duration == "annually":
            expiry_date = (datetime.date.today() + relativedelta(years=1)).strftime(
                "%Y-%m-%d"
            )

        # get payment for paypal that matched the orderID
        requestorder = OrdersGetRequest(data)
        response = PPClient.client.execute(requestorder)

        # every user has a free subscription, update that
        subscription = models.Subscription.objects.filter(user=request.user.id, package_id=package_id).first()
        
        subscription.pricing=models.Pricing.objects.filter(id=pricing_id).first()
        subscription.expiry_date=expiry_date
        subscription.total_amount_paid=float(response.result.purchase_units[0].amount.value)
        subscription.email=response.result.payer.email_address
        subscription.address=response.result.purchase_units[0].shipping.address.address_line_1
        subscription.country_code=response.result.purchase_units[
            0
        ].shipping.address.country_code
        subscription.order_key=response.result.id
        
        subscription.save()

        if subscription:
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=500)

@login_required
def Profile(request):
    context_data = {
        'user': request.user,
        "subscriptions": models.Subscription.objects.filter(
            user=request.user.id
        ).order_by("-id")
    }
    return render(request, template_name='profile.html', context=context_data)