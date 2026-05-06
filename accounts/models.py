from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=True)


class CarType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    distance = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pickup_location} → {self.drop_location}"


class Fare(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('route', 'car_type')


class Schedule(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    available_date = models.DateField()
    available_time = models.TimeField(null=True, blank=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)


class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True, blank=True)
    travel_date = models.DateField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    enquiry = models.OneToOneField(Enquiry, on_delete=models.CASCADE)
    confirmed_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='CONFIRMED')


class Driver(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=100)
    assigned_car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True)
    is_available = models.BooleanField(default=True)


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='PENDING')
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)