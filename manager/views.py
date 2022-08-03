from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from manager import models
from django.utils import timezone
import datetime

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

        if request.COOKIES.get('user_type'):
            return redirect(reverse("app_auth:login_complete", kwargs={'source': 'extension'}))

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
            return redirect(reverse("app_auth:login"))

        package = models.Package.objects.filter(slug=slug).first()

        context_data = {
            "package": package,
            "pricings": models.Pricing.objects.filter(package=package),
            "features": models.Feature.objects.filter(package=package),
        }

        return render(request, self.template_name, context=context_data)


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
        total_price = int(price_obj.price)

        if payment_duration == "annually":
            total_price = price_obj.annualy_price

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

        subcription = models.Subscription(
            user=request.user.id,
            user_type=request.user.__class__.__name__,
            package_id=models.Package.objects.filter(id=package_id).first(),
            pricing=models.Pricing.objects.filter(id=pricing_id).first(),
            expiry_date=expiry_date,
            total_amount_paid=float(response.result.purchase_units[0].amount.value),
            email=response.result.payer.email_address,
            address=response.result.purchase_units[0].shipping.address.address_line_1,
            country_code=response.result.purchase_units[
                0
            ].shipping.address.country_code,
            order_key=response.result.id,
        )
        subcription.save()

        if subcription:
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=500)
