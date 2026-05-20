from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chauffer.api.views import *

router = DefaultRouter()
router.register('car-types', CarTypeViewSet)
router.register('routes', RouteViewSet)
router.register('fares', FareViewSet)
router.register('recurring-schedules', RecurringScheduleViewSet)
router.register('schedule-exceptions', ScheduleExceptionViewSet)
router.register('enquiries', EnquiryViewSet)
router.register('bookings', BookingViewSet)
router.register('drivers', DriverViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]