from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from manager import models

import json
import datetime
from dateutil.relativedelta import relativedelta

from paypalcheckoutsdk.orders import OrdersGetRequest
from .paypal import PayPalClient

# Create your views here.
class HomePageView(View):
    template_name = 'userDashboard.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('app_auth:login'))


        context_data = {
            'packages' : models.Package.objects.all().order_by('-id')
        }

        return render(request, self.template_name, context=context_data)

class PackageDetailView(View):
    template_name = 'package.html'

    def get(self, request, slug):
        if not request.user.is_authenticated:
            return redirect(reverse('app_auth:login'))

        package = models.Package.objects.filter(slug=slug).first()

        context_data = {
            'package' : package,
            'pricings' : models.Pricing.objects.filter(package=package),
            'features' : models.Feature.objects.filter(package=package),
        }


        return render(request, self.template_name, context=context_data)

class PaymentView(View):
    template_name = 'payment.html'

    def get(self):
        return redirect(reverse('manager:dashboard'))

    def post(self, request, *args, **kwargs):

        package_id = request.POST.get('package_id', '')
        pricing_id = request.POST.get('pricing_id', '')
        payment_duration = request.POST.get('payment_duration', '')

        # calculate total price
        price_obj = models.Pricing.objects.filter(id=pricing_id).first()
        total_price = int(price_obj.price)

        if payment_duration == 'annually':
            total_price = total_price * 12

        context_data = {
            'package_id' : package_id,
            'total_price' : total_price,
            'subscription_duration' : payment_duration,
        }

        return render(request, self.template_name, context=context_data)

class CompletePaymentView(View):
    def post(self, request, *args, **kwargs):

        PPClient = PayPalClient()

        body = json.loads(request,body)

        data = body['orderID']
        package_id = body['package_id']
        subscription_duration = body['subscription_duration']


        expiry_date = (datetime.date.today () + relativedelta (months=1)).strftime ('%Y-%m-%d')

        if subscription_duration == "annually":
            expiry_date = (datetime.date.today () + relativedelta (years=1)).strftime ("%Y-%m-%d"),

        user_id = request.user.id

        # get payment for paypal that matched the orderID
        requestorder = OrdersGetRequest(data)
        response = PPClient.client.execute(requestorder)

        models.Subscription.objects.create(
            user_id = user_id,
            package_id = package_id,
            start_date = datetime.date.today().strftime ("%Y-%m-%d"),
            expiry_date =  expiry_date,
            total_paid = response.result.purchase_units[0].amount.value,
            email = response.result.payer.email_address,
            address = response.result.purchase_units[0].shipping.address.address_line_1,
            country_code = response.result.purchase_units[0].shipping.address.country_code,
            order_key = response.result.id
        )