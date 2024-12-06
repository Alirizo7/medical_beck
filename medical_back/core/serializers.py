from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Doctor, Medication, Patient, Procedure, Appointment, CustomUser, Anamesis

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
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=6)
    birth_date = serializers.DateField(required=False)
    phone_number = serializers.CharField(max_length=15, required=False)

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )

        Doctor.objects.create(
            user=user,
            phone_number=validated_data['phone_number']
        )

        return user


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserPostSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'birth_date', 'phone_number']

    def update(self, instance, validated_data):
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


class AnamesisSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=False)

    class Meta:
        model = Anamesis
        fields = ['id', 'name', 'description', 'patient']


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ['id', 'doctor', 'date', 'name', 'details', 'patient', 'image']
        read_only_fields = ['doctor']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.details = validated_data.get('details', instance.details)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'phone_number', 'comment', 'is_contact', 'birth_date']


class AppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), source='patient', write_only=True)
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'name', 'date', 'time_from', 'time_to', 'patient', 'patient_id', 'comment']
