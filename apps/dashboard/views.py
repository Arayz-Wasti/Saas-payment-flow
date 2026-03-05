from rest_framework import views, response, permissions
from apps.core.permissions import IsSubscribed

class PremiumDashboardView(views.APIView):
    """
    A sample API endpoint that requires an active subscription.
    """
    permission_classes = [permissions.IsAuthenticated, IsSubscribed]

    def get(self, request):
        return response.Response({
            'message': 'Welcome to the Premium Dashboard!',
            'data': 'This information is only visible to active subscribers.'
        })
