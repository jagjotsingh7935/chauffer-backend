from rest_framework import serializers
from chauffer.models import *

class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class FareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fare
        fields = '__all__'


class RecurringScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringSchedule
        fields = '__all__'


class ScheduleExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleException
        fields = '__all__'


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'age']


class EnquirySerializer(serializers.ModelSerializer):
    additional_passengers = PassengerSerializer(many=True, required=False)

    class Meta:
        model = Enquiry
        fields = '__all__'
        read_only_fields = ['status', 'rejection_reason', 'booked_price', 'created_at']

    def create(self, validated_data):
        passengers_data = validated_data.pop('additional_passengers', [])
        enquiry = Enquiry.objects.create(**validated_data)
        for p_data in passengers_data:
            Passenger.objects.create(enquiry=enquiry, **p_data)
        return enquiry

    def update(self, instance, validated_data):
        passengers_data = validated_data.pop('additional_passengers', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if passengers_data is not None:
            instance.additional_passengers.all().delete()
            for p_data in passengers_data:
                Passenger.objects.create(enquiry=instance, **p_data)
        return instance


class BookingSerializer(serializers.ModelSerializer):
    enquiry = EnquirySerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'