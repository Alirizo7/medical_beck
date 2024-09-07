# urls.py

from django.urls import path
from .views import register_doctor, login_doctor, MedicationListView, get_user_profile, update_user_profile, \
    manage_patients, update_patient, ProcedureListCreateAPIView

urlpatterns = [
    path('register/', register_doctor, name='register_doctor'),
    path('login/', login_doctor, name='login_doctor'),
    path('medications/', MedicationListView.as_view(), name='medication-list'),
    path('register/', register_doctor, name='register_doctor'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('edit-profile/', update_user_profile, name='get_user_profile'),
    path('patients/', manage_patients, name='manage_patients'),
    path('patients/<int:patient_id>/', update_patient, name='update_patient'),
    path('procedures/', ProcedureListCreateAPIView.as_view(), name='procedure-list-create'),
    path('procedures/<int:patient_id>/', ProcedureListCreateAPIView.as_view(), name='procedure-list-by-patient'),

]
