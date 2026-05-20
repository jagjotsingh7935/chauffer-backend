from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail
from django.conf import settings
from chauffer.models import *
from chauffer.api.serializers import *

class StandardPagination(PageNumberPagination):
    page_size = 10


class CarTypeViewSet(viewsets.ModelViewSet):
    queryset = CarType.objects.all()
    serializer_class = CarTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pickup_location', 'drop_location']


class FareViewSet(viewsets.ModelViewSet):
    queryset = Fare.objects.all()
    serializer_class = FareSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['route', 'car_type']


class RecurringScheduleViewSet(viewsets.ModelViewSet):
    queryset = RecurringSchedule.objects.all()
    serializer_class = RecurringScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['route', 'car_type', 'day_of_week']


class ScheduleExceptionViewSet(viewsets.ModelViewSet):
    queryset = ScheduleException.objects.all()
    serializer_class = ScheduleExceptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['route', 'car_type', 'exception_date']


class EnquiryViewSet(viewsets.ModelViewSet):
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'travel_date']

    def get_permissions(self):
        if self.action == 'create':
            return []  # public
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        enquiry = serializer.save()
        # Send email to admin
        self._send_admin_alert(enquiry)
        # Send confirmation to user
        self._send_user_confirmation(enquiry)

    def _send_admin_alert(self, enquiry):
        subject = "New Taxi Enquiry Received"
        message = f"""
        New enquiry from {enquiry.name}
        Pickup: {enquiry.pickup_location}
        Drop: {enquiry.drop_location}
        Date: {enquiry.travel_date} {enquiry.travel_time}
        Proposed price: {enquiry.proposed_price or 'Not specified'}
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL], fail_silently=True)

    def _send_user_confirmation(self, enquiry):
        subject = "We have received your enquiry"
        message = f"Dear {enquiry.name},\n\nThank you for booking with us. Your enquiry ID is #{enquiry.id}. We will get back to you soon."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [enquiry.email], fail_silently=True)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        enquiry = self.get_object()
        if enquiry.status != 'PENDING':
            return Response({"error": "Enquiry already processed"}, status=400)

        # Get price: if not provided in request, use proposed_price or fallback
        booked_price = request.data.get('booked_price')
        if not booked_price:
            booked_price = enquiry.proposed_price
        if not booked_price:
            return Response({"error": "booked_price is required"}, status=400)

        enquiry.status = 'ACCEPTED'
        enquiry.booked_price = booked_price
        enquiry.rejection_reason = ''
        driver_id = request.data.get('driver_id')
        if driver_id:
            enquiry.driver_id = driver_id
        enquiry.save()

        # Create booking
        Booking.objects.create(enquiry=enquiry, confirmed_price=booked_price)

        # Send acceptance email
        self._send_accept_reject_email(enquiry, 'ACCEPTED')
        return Response({"message": "Enquiry accepted", "booked_price": str(booked_price)})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        enquiry = self.get_object()
        if enquiry.status != 'PENDING':
            return Response({"error": "Enquiry already processed"}, status=400)

        reason = request.data.get('reason', 'No reason provided')
        enquiry.status = 'REJECTED'
        enquiry.rejection_reason = reason
        enquiry.save()

        self._send_accept_reject_email(enquiry, 'REJECTED', reason)
        return Response({"message": "Enquiry rejected"})

    def _send_accept_reject_email(self, enquiry, status, reason=""):
        if status == 'ACCEPTED':
            subject = "Booking Confirmed"
            message = f"""
            Dear {enquiry.name},
            Your booking has been ACCEPTED.
            Final price: ₹{enquiry.booked_price}
            Driver: {enquiry.driver.name if enquiry.driver else 'To be assigned'}
            Date: {enquiry.travel_date} {enquiry.travel_time}
            """
        else:
            subject = "Booking Update"
            message = f"""
            Dear {enquiry.name},
            Your booking request has been REJECTED.
            Reason: {reason}
            """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [enquiry.email], fail_silently=True)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_available']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_status']