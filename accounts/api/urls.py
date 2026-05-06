from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register('car-types', CarTypeViewSet)
router.register('routes', RouteViewSet)
router.register('fares', FareViewSet)
router.register('schedules', ScheduleViewSet)
router.register('enquiries', EnquiryViewSet)
router.register('bookings', BookingViewSet)
router.register('drivers', DriverViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]