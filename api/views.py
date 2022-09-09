from rest_framework.views import APIView
from manager.models import Subscription, Package, Pricing
from rest_framework.response import Response

from app_auth import models as AuthModels

class AliExpressSubcriptionRetrieveView(APIView):
    """
        view recieves
            user
    """
    def get(self, request, *args, **kwargs):
        response = dict()

        user_id = request.user.id
        response['results'] = list()

        subscriptions = Subscription.objects.filter(user=user_id, package_id__name='Aliexpress Media Downloader', user_type=request.user.__class__.__name__)
        user = AuthModels.User.objects.filter(id=user_id).first()

        package = Package.objects.filter(name="Aliexpress Media Downloader").first()

        for subscription in subscriptions:
            response = dict()
            response['user'] = {
                "username": user.username,
            }
            response['package'] = package.name
            response['pricing'] = subscription.pricing.name
            response['features'] = [feature.name for feature in subscription.pricing.pricing_feature.all()]       

        return Response(response)
        