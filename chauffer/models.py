from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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


class RecurringSchedule(models.Model):
    """Lifelong schedule: repeats weekly on specific days"""
    WEEKDAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('route', 'car_type', 'day_of_week')


class ScheduleException(models.Model):
    """Exception for a specific date (e.g., unavailable or different price)"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    exception_date = models.DateField()
    is_available = models.BooleanField(default=True)  # False means unavailable
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('route', 'car_type', 'exception_date')


class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    # Main contact details
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    # Journey details
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    travel_date = models.DateField()
    travel_time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True, help_text="Short description or special requests")

    # Optional: user can propose a price
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # System fields
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)  # null for custom route
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True)  # admin can assign

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True)  # reason if rejected
    booked_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # final price when accepted

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry #{self.id} - {self.name} ({self.status})"


class Passenger(models.Model):
    """Additional passengers travelling with the main customer"""
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='additional_passengers')
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Age {self.age})"


class Booking(models.Model):
    enquiry = models.OneToOneField(Enquiry, on_delete=models.CASCADE)
    confirmed_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='CONFIRMED')

    def __str__(self):
        return f"Booking #{self.id} - {self.enquiry.name}"


class Driver(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=100)
    assigned_car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='PENDING')
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)