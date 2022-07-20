from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from manager import models

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