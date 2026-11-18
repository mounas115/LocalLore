
from django.db import models


class Guide(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(default=0)
    description = models.TextField()
    available = models.BooleanField(default=True)
    max_group_size = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name


class Attraction(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=100)
    description = models.TextField()
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    tourist_name = models.CharField(max_length=100)
    guide = models.ForeignKey(
        Guide, on_delete=models.CASCADE, related_name="bookings"
    )
    booking_date = models.DateField()
    group_size = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.tourist_name} - {self.guide.name}"

