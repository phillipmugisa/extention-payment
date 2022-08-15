from re import S
from rest_framework.views import APIView
from manager.models import Subscription, Package, Pricing
from rest_framework.response import Response

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

        package = Package.objects.filter(name="Aliexpress Media Downloader").first()

        if subscriptions:
            for subscription in subscriptions:
                response = dict()
                response['user'] = subscription.user
                response['package'] = package.name
                response['pricing'] = subscription.pricing.name
                response['features'] = [feature.name for feature in subscription.pricing.pricing_feature.all()]
        else:
            response = dict()
            response['user'] = user_id
            response['package'] = package.name
            response['pricing'] = 'Free'
            response['features'] = [feature.name for feature in Pricing.objects.filter(name='Free').first().pricing_feature.all().filter(package=package)]            

        return Response(response)