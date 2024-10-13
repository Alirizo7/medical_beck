# urls.py

from django.urls import path
from .views import register_doctor, login_doctor, get_user_profile, update_user_profile, \
    manage_patients, update_patient, ProcedureListCreateAPIView, MedicationAPIView, MedicationDetailUpdateAPIView, \
    MedicationCreateAPIView, AppointmentAPIView, AppointmentDetailAPIView, ProcedureDetailAPIView, AnamesisAPIView, \
    AnamesisDetailAPIView, UploadProcedureImageAPIView, DeleteProcedureImageAPIView, ProcedureImagesAPIView, \
    AnamesisPatientIdAPIView, request_verification_code, verify_code, change_password

urlpatterns = [
    path('register/', register_doctor, name='register_doctor'),
    path('login/', login_doctor, name='login_doctor'),
    path('medications/', MedicationAPIView.as_view(), name='medication-list'),
    path('medications-create/', MedicationCreateAPIView.as_view(), name='medication-list-create'),
    path('medications/<int:pk>/', MedicationDetailUpdateAPIView.as_view(), name='medication-detail-update'),
    path('register/', register_doctor, name='register_doctor'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('edit-profile/', update_user_profile, name='get_user_profile'),
    path('patients/', manage_patients, name='manage_patients'),
    path('patients/<int:patient_id>/', update_patient, name='update_patient'),
    path('procedures/', ProcedureListCreateAPIView.as_view(), name='procedure-list-create'),
    path('procedures/<int:patient_id>/', ProcedureListCreateAPIView.as_view(), name='procedure-list-by-patient'),
    path('procedures_update/<int:pk>/', ProcedureDetailAPIView.as_view(), name='procedure-detail'),
    path('appointments/', AppointmentAPIView.as_view(), name='appointments-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailAPIView.as_view(), name='appointment-detail'),

    path('anamesis/', AnamesisAPIView.as_view(), name='anamesis-list'),
    path('anamesis_get/<patient_id>/', AnamesisPatientIdAPIView.as_view(), name='anamesis-patient-list'),
    path('anamesis/<int:pk>/', AnamesisDetailAPIView.as_view(), name='anamesis-detail-update'),

    path('procedures/<int:pk>/images/', ProcedureImagesAPIView.as_view(), name='procedure-images'),
    path('procedures/<int:pk>/upload-images/', UploadProcedureImageAPIView.as_view(), name='upload-procedure-images'),
    path('procedures/<int:pk>/images/<int:image_id>/delete/', DeleteProcedureImageAPIView.as_view(),
         name='delete-procedure-image'),

    path('request-verification/', request_verification_code, name='request_verification_code'),
    path('verify-code/', verify_code, name='verify_code'),
    path('change-password/', change_password, name='change_password'),
]
