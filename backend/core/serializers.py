from rest_framework import serializers
from .models import Guide, Attraction, Booking


class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = "__all__"


class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, data):
        guide = data.get("guide")
        group_size = data.get("group_size")

        if guide and not guide.available:
            raise serializers.ValidationError(
                "This guide is currently unavailable."
            )

        if guide and group_size > guide.max_group_size:
            raise serializers.ValidationError(
                "Group size exceeds the guide's maximum capacity."
            )

        return data