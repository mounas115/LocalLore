
from rest_framework import viewsets
from .models import Guide, Attraction, Booking
from .serializers import (
    GuideSerializer,
    AttractionSerializer,
    BookingSerializer,
)


class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer


class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


import os

from google import genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ItineraryView(APIView):

    def post(self, request):
        destination = request.data.get("destination", "").strip()
        days = request.data.get("days", 1)
        preference = request.data.get("preference", "general")

        if not destination:
            return Response(
                {"error": "Destination is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            days = int(days)
            if days < 1 or days > 7:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {"error": "Days must be between 1 and 7."},
                status=status.HTTP_400_BAD_REQUEST
            )

        attractions = Attraction.objects.filter(
            location__icontains=destination
        )

        if not attractions.exists():
            return Response(
                {"error": "No listed attractions found for this destination."},
                status=status.HTTP_404_NOT_FOUND
            )

        attraction_data = []

        for attraction in attractions:
            attraction_data.append({
        "name": attraction.name,
        "location": attraction.location,
        "description": attraction.description,
        "opening_time": (
            attraction.opening_time.strftime("%H:%M")
            if attraction.opening_time else "Not available"
        ),
        "closing_time": (
            attraction.closing_time.strftime("%H:%M")
            if attraction.closing_time else "Not available"
        ),
    })

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return Response(
                {"error": "Gemini API key is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        

        prompt = f"""
You are LocalLore, an intelligent tourism itinerary assistant.

Create a practical {days}-day itinerary for {destination}.
Travel preference: {preference}.

Use ONLY the attractions provided in the database below.
Never invent or add attractions.

DATABASE ATTRACTIONS:
{attraction_data}

IMPORTANT RULES:

1. Use only the database-listed attractions.
2. Respect the opening and closing times of every attraction.
3. Organise the itinerary day by day.
4. Include suggested visit times for each attraction.
5. Match the user's travel preference as closely as possible.
6. Do not describe a nature attraction as a heritage attraction or vice versa.
7. Do not repeat attractions unnecessarily.
8. Do not invent prices, distances, travel times or booking availability.
9. Do not claim that opening hours have been independently verified.
10. If there are fewer attractions than needed for the requested number of days, explain this briefly.
11. Do not claim there are too few attractions merely because they cannot fill an entire day.
12. If there are not enough attractions for a full day, provide a shorter, realistic itinerary.
13. Use the actual attraction descriptions provided in the database.

FORMAT:

### Day 1: [Theme]

**Time – Time | Attraction Name**
- Description:
- Suggested activity:

Continue for each requested day.

End with a short practical note if necessary.

Make the itinerary clear, realistic and easy to follow.
"""

        try:
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return Response({
                "destination": destination,
                "days": days,
                "preference": preference,
                "available_attractions": attraction_data,
                "itinerary": response.text
            })

        except Exception as error:
            return Response(
                {"error": f"Gemini generation failed: {str(error)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )
