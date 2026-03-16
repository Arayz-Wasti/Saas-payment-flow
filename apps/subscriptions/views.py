from rest_framework import generics, permissions
from .models import Plan
from .serializers import PlanSerializer


class PlanListView(generics.ListAPIView):
    """Public endpoint to list all active subscription plans."""
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Plan.objects.filter(is_active=True).order_by('price')
