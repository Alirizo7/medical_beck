from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Doctor, Medication, Patient, Procedure, Appointment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['birth_date', 'phone_number']


class RegisterDoctorSerializer(serializers.Serializer):
    user = UserSerializer()
    doctor = DoctorSerializer()

    def create(self, validated_data):
        user_data = validated_data['user']
        doctor_data = validated_data['doctor']

        # Create the user
        user = User.objects.create_user(**user_data)

        # Create the doctor's profile
        Doctor.objects.create(user=user, **doctor_data)

        return user

    def to_internal_value(self, data):
        # This method ensures that nested serializers are handled properly
        user_data = data.get('user')
        doctor_data = data.get('doctor')

        if not user_data:
            raise serializers.ValidationError({'user': 'This field is required.'})
        if not doctor_data:
            raise serializers.ValidationError({'doctor': 'This field is required.'})

        # Pass nested data to their respective serializers
        user_serializer = UserSerializer(data=user_data)
        doctor_serializer = DoctorSerializer(data=doctor_data)

        user_serializer.is_valid(raise_exception=True)
        doctor_serializer.is_valid(raise_exception=True)

        return {
            'user': user_serializer.validated_data,
            'doctor': doctor_serializer.validated_data
        }


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['birth_date', 'phone_number']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserPostSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'birth_date', 'phone_number']

    def update(self, instance, validated_data):
        # Данные для пользователя (email, first_name, last_name)
        user_data = validated_data.pop('user', None)

        if user_data:
            user = instance.user
            for field, value in user_data.items():
                setattr(user, field, value)
            user.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            return {
                'user': user,
                'access': str(RefreshToken.for_user(user).access_token),
                'refresh': str(RefreshToken.for_user(user))
            }
        raise serializers.ValidationError('Both email and password are required')


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'quantity']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'phone_number', 'comment', 'is_contact']


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ['id', 'doctor', 'date', 'name', 'patient', 'details']
        read_only_fields = ['doctor']


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)  # Вложенный сериализатор для пациента

    class Meta:
        model = Appointment
        fields = ['id', 'name', 'date', 'time_from', 'time_to', 'patient', 'comment']
