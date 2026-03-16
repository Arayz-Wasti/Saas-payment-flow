from rest_framework import serializers
from .models import Plan


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for public Plan listing."""

    class Meta:
        model = Plan
        fields = ('id', 'name', 'description', 'price', 'currency', 'interval', 'trial_days', 'features')
