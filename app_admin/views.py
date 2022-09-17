from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import View, generic
from django.contrib import messages

from manager import models as ManagerModels
from app_auth import models as AuthModels

from app_admin.mixins import SupportOnlyAccessMixin

class AdminManagersView(SupportOnlyAccessMixin, View):
    template_name = "app_admin/manager.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = "Admin Dashboard"
        context_data["active_tab"] = "Manager"
        context_data["statistics"] = {
            "context_name": "statistics",
            "results": [
                {
                    "name": "Total Users",
                    "description": "Total User Count",
                    "count": AuthModels.User.objects.filter(is_superuser=False).count(),
                },
                {
                    "name": "Total Subscriptions",
                    "description": "Total Subscriptin Count",
                    "count": ManagerModels.Subscription.objects.all().count(),
                },
                {
                    "name": "Total Packages",
                    "description": "Total Package Count",
                    "count": ManagerModels.Package.objects.all().count(),
                },
                {
                    "name": "Total Features",
                    "description": "Total Feature Count",
                    "count": ManagerModels.Feature.objects.all().count(),
                }
            ],
        }

        return context_data

class AdminSubscriptionListView(SupportOnlyAccessMixin, View):
    model = ManagerModels.Subscription
    template_name = "app_admin/subscriptions.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = "Admin Dashboard"
        context_data["active_tab"] = "Manager"
        context_data["subscriptions"] = {
            "context_name": "subscriptions",
            "results": [
                {
                    "user": AuthModels.User.objects.filter(pk=subscription.user).first(),
                    "subscription" : subscription
                }
                for subscription in self.model.objects.all()
            ]
        }

        return context_data


class AdminUserListView(SupportOnlyAccessMixin, View):
    model = AuthModels.User
    template_name = "app_admin/users.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = "Admin Dashboard"
        context_data["active_tab"] = "Manager"
        context_data["users"] = {
            "context_name": "users",
            "results": self.model.objects.filter(is_superuser=False),
        }

        return context_data

class AdminServiceListView(SupportOnlyAccessMixin, View):
    model = ManagerModels.Package
    template_name = "app_admin/services.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = "Admin Dashboard"
        context_data["active_tab"] = "Manager"
        context_data["services"] = {
            "context_name": "services",
            "results": self.model.objects.all()
        }

        return context_data

class AdminPricingListView(SupportOnlyAccessMixin, generic.ListView):
    model = ManagerModels.Pricing
    template_name = "app_admin/pricing_list.html"


class FeatureCreateView(SupportOnlyAccessMixin, View):
    template_name = "app_admin/feature_create.html"

    def post(self, request):
        package_name = request.POST.get("service_name")
        package_description = request.POST.get("service_description")
        package_image = request.POST.get("service_image")

        try:
            package = ManagerModels.Package.objects.filter(name=package_name)
            if package.exists():
                messages.add_message(
                    request, messages.ERROR, _(f"Category({package_name}) already exists.")
                )
                return redirect(reverse("app_admin:features-create"))
            
            package = ManagerModels.Package.objects.create(name=package_name, description=package_description, img_url=package_image)

            for feature_key in [obj_key for obj_key in request.POST.keys() if "feature" in obj_key]:
                feature_name = request.POST.get(f"{feature_key}")

                if ManagerModels.Feature.objects.filter(
                    name=feature_name
                ).exists():
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Feature ({feature_name}) already exists.",
                    )
                    continue

                ManagerModels.Feature.objects.create(
                    name=feature_name,
                    package=package

                )
            messages.add_message(
                request, messages.SUCCESS, "Created Successfully"
            )
        except:
            package = ManagerModels.Package.objects.filter(name=package_name).first()
            if package:
                package.delete()
            messages.add_message(
                request, messages.ERROR, "An Error Occured. Please Try Again"
            )

        return redirect(reverse("app_admin:features-create"))

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self, **kwargs):
        context_data = dict()
        context_data["view_name"] = "Admin Dashboard"
        context_data["active_tab"] = "Manager"
        return context_data



class PricingCreateView(SupportOnlyAccessMixin, View):
    template_name = "app_admin/pricing_create.html"

    def post(self, request):
        pricing_name = request.POST.get("pricing_name")
        pricing_monthly_charge = int(request.POST.get("pricing_monthly_charge"))
        annual_charge = int(request.POST.get("pricing_annual_charge"))
        pricing_package = request.POST.get("pricing_package")

        try:
            pricing = ManagerModels.Pricing.objects.filter(name=pricing_name, package__name=pricing_package)
            if pricing.exists():
                messages.add_message(
                    request, messages.ERROR, f"Pricing ({pricing_name}) already exists."
                )
                return redirect(reverse("app_admin:pricing-create"))

            package = ManagerModels.Package.objects.filter(name=pricing_package)
            if not package:
                messages.add_message(
                    request, messages.ERROR, f"Service ({pricing_package}) not found. Please Create Service to continue."
                )
                return redirect(reverse("app_admin:pricing-create"))
            
            pricing = ManagerModels.Pricing.objects.create(name=pricing_name, price=pricing_monthly_charge, annualy_price=annual_charge, package=package.first())

            for feature_key in [obj_key for obj_key in request.POST.keys() if "feature" in obj_key]:
                feature_name = request.POST.get(f"{feature_key}")
                feature = ManagerModels.Feature.objects.filter(name=feature_name)
                if not feature:
                    feature = ManagerModels.Feature.objects.create(
                        name=feature_name,
                        package=package.first()

                    )
                    messages.add_message(
                        request, messages.INFO, f"Pricing Feature ({feature_name}) created and added to package {package.first().name}."
                    )
                else:
                    feature = feature.first()

                pricing.pricing_feature.add(feature)

                feature.save()
            messages.add_message(
                request, messages.SUCCESS, "Created Successfully"
            )
        except Exception as Err:
            pricing = ManagerModels.Package.objects.filter(name=pricing_name).first()
            if pricing:
                pricing.delete()
            messages.add_message(
                request, messages.ERROR, f"An Error Occured. Please Try Again {Err}"
            )

        return redirect(reverse("app_admin:pricing-create"))

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self, **kwargs):
        context_data = dict()
        context_data["view_name"] = "Admin Dashboard"
        context_data["active_tab"] = "Manager"
        context_data["packages"] = ManagerModels.Package.objects.all()
        context_data["features"] = ManagerModels.Feature.objects.all()
        return context_data
