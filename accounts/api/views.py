from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .utils import send_enquiry_email
from accounts.models import *
from .serializers import *


class StandardPagination(PageNumberPagination):
    page_size = 10


class CarTypeViewSet(viewsets.ModelViewSet):
    queryset = CarType.objects.all()
    serializer_class = CarTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pickup_location', 'drop_location']


class FareViewSet(viewsets.ModelViewSet):
    queryset = Fare.objects.all()
    serializer_class = FareSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['route', 'car_type']


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['route', 'car_type', 'available_date']


class EnquiryViewSet(viewsets.ModelViewSet):
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'travel_date']

    def get_permissions(self):
        if self.action == 'create':
            return []
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        enquiry = self.get_object()
        enquiry.status = 'ACCEPTED'
        enquiry.save()

        Booking.objects.create(
            enquiry=enquiry,
            confirmed_price=100  # replace with logic
        )

        return Response({"message": "Enquiry accepted"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        enquiry = self.get_object()
        enquiry.status = 'REJECTED'
        enquiry.save()

        return Response({"message": "Enquiry rejected"})


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_available']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_status']





@action(detail=True, methods=['post'])
def accept(self, request, pk=None):
    enquiry = self.get_object()
    enquiry.status = 'ACCEPTED'
    enquiry.save()

    Booking.objects.create(
        enquiry=enquiry,
        confirmed_price=100  # replace with real logic
    )

    send_enquiry_email(enquiry, "ACCEPTED")

    return Response({"message": "Enquiry accepted & email sent"})





@action(detail=True, methods=['post'])
def reject(self, request, pk=None):
    enquiry = self.get_object()
    enquiry.status = 'REJECTED'
    enquiry.save()

    send_enquiry_email(enquiry, "REJECTED")

    return Response({"message": "Enquiry rejected & email sent"})