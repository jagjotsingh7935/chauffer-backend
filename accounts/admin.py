from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(CarType)
admin.site.register(Route)
admin.site.register(Fare)
admin.site.register(Schedule)
admin.site.register(Enquiry)
admin.site.register(Booking)
admin.site.register(Driver)
admin.site.register(Payment)