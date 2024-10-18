from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.utils import timezone
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import requests

from .models import Medication, Doctor, Patient, Procedure, Appointment, Anamesis, Images, CustomUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import LoginSerializer, MedicationSerializer, ProfileSerializer, \
    PatientSerializer, ProcedureSerializer, RegisterDoctorSerializer, AppointmentSerializer, AnamesisSerializer
from .utils import generate_verification_code, send_verification_email


@api_view(['POST'])
def register_doctor(request):
    serializer = RegisterDoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_doctor(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        return Response({
            'access': data['access'],
            'refresh': data['refresh']
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicationAPIView(APIView):

    def get(self, request):
        user = request.user
        medications = Medication.objects.filter(doctor__user=user)
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MedicationCreateAPIView(APIView):
    def post(self, request):
        serializer = MedicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=request.user.doctor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicationDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Medication.objects.get(pk=pk, doctor__user=self.request.user)
        except Medication.DoesNotExist:
            return None

    def get(self, request, pk):
        medication = self.get_object(pk)
        if not medication:
            return Response({'error': 'Препарат не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicationSerializer(medication)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        medication = self.get_object(pk)
        if not medication:
            return Response({'error': 'Препарат не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicationSerializer(medication, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    try:
        doctor_profile = user.doctor_profile
        serializer = ProfileSerializer(doctor_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Doctor.DoesNotExist:
        return Response({"error": "Профиль доктора не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user

    try:
        doctor_profile = user.doctor_profile

        serializer = ProfileSerializer(instance=doctor_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Doctor.DoesNotExist:
        return Response({"error": "Профиль доктора не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_patients(request):
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response({'error': 'Профиль доктора не найден'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        search_query = request.GET.get('search', None)
        if search_query:
            patients = Patient.objects.filter(doctor=doctor, last_name__icontains=search_query)
        else:
            patients = Patient.objects.filter(doctor=doctor)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        serializer = PatientSerializer(data=data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_patient(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({'error': 'Пациент не найден'}, 404)

    serializer = PatientSerializer(patient, data=request.data,
                                   partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, 400)


class UpdatePatientView(APIView):

    def put(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(doctor=request.user.doctor_profile)
            return Response(serializer.data, 200)
        return Response(serializer.errors, 400)


class ProcedureListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id=None):
        if patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
            procedures = Procedure.objects.filter(patient=patient).order_by('-date')
        else:
            procedures = Procedure.objects.all().order_by('-date')

        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProcedureSerializer(data=request.data)
        if serializer.is_valid():
            doctor = getattr(request.user, 'doctor_profile', None)
            if not doctor:
                return Response({"detail": "Доктор не найден для данного пользователя."},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcedureDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        serializer = ProcedureSerializer(procedure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        serializer = ProcedureSerializer(procedure, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        appointments = Appointment.objects.filter(doctor=request.user.doctor_profile, date__gte=today)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=request.user.doctor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk, doctor=self.request.user.doctor_profile)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        appointment = self.get_object(pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    def put(self, request, pk):
        appointment = self.get_object(pk)
        serializer = AppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnamesisAPIView(APIView):

    def get(self, request):
        user = request.user
        anamesis = Anamesis.objects.filter(doctor__user=user)
        serializer = AnamesisSerializer(anamesis, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AnamesisSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=request.user.doctor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnamesisPatientIdAPIView(APIView):

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id)
        anamesis = Anamesis.objects.filter(patient=patient)
        print(anamesis)
        serializer = AnamesisSerializer(anamesis, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnamesisDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Anamesis.objects.get(pk=pk, doctor__user=self.request.user)
        except Anamesis.DoesNotExist:
            return None

    def get(self, request, pk):
        anamesis = self.get_object(pk)
        if not anamesis:
            return Response({'error': 'Препарат не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnamesisSerializer(anamesis)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        anamesis = self.get_object(pk)
        if not anamesis:
            return Response({'error': 'Препарат не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnamesisSerializer(anamesis, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadProcedureImageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        files = request.FILES.getlist('images')

        if not files:
            return Response({"error": "Нет изображений для загрузки"}, status=status.HTTP_400_BAD_REQUEST)

        for file in files:
            Images.objects.create(procedure=procedure, thumbnail=file)

        return Response({"success": "Изображения успешно загружены"}, status=status.HTTP_201_CREATED)


class DeleteProcedureImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, image_id):
        try:
            image = Images.objects.get(pk=image_id, procedure_id=pk)
            image.thumbnail.delete()
            image.delete()
            return Response({"success": "Изображение успешно удалено"}, status=status.HTTP_204_NO_CONTENT)
        except Images.DoesNotExist:
            return Response({"error": "Изображение не найдено"}, status=status.HTTP_404_NOT_FOUND)


class ProcedureImagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        images = Images.objects.filter(procedure=procedure)
        images_data = [{'id': img.id, 'url': img.thumbnail.url} for img in images]
        return Response(images_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def request_verification_code(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required."}, 400)

    code = generate_verification_code()

    request.session['verification_code'] = code
    request.session['email'] = email

    if send_verification_email(email, code):
        return Response({"success": "Verification code sent."}, 200)
    else:
        return Response({"error": "Failed to send verification email."}, 500)


@api_view(['POST'])
def verify_code(request):
    email = request.data.get('email')
    code = request.data.get('code')

    stored_code = request.session.get('verification_code')
    stored_email = request.session.get('email')

    if email != stored_email:
        return Response({"error": "Email does not match."}, 400)

    if code != stored_code:
        return Response({"error": "Invalid verification code."}, 400)

    request.session.pop('verification_code')
    request.session.pop('email')

    return Response({"success": "Email verified."}, 200)


@api_view(['POST'])
def change_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if new_password != confirm_password:
        return Response({"error": "Пароли не совпадают"}, 400)

    try:
        user = CustomUser.objects.get(email=email)
        user.password = make_password(new_password)
        user.save()
        return Response({"success": "Пароль успешно изменен"}, 200)
    except CustomUser.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, 404)
