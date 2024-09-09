from django.contrib import admin
from .models import CustomUser, Doctor, Patient, Medication, Procedure, Appointment, Anamesis


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'phone_number')
    search_fields = ('user__email', 'user__last_name', 'user__first_name')
    list_filter = ('birth_date',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'phone_number', 'doctor')
    search_fields = ('last_name', 'first_name', 'phone_number', 'doctor__user__email')
    list_filter = ('doctor',)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'doctor')
    search_fields = ('name', 'doctor__user__email')
    list_filter = ('doctor',)


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'patient', 'doctor')
    search_fields = ('name', 'patient__last_name', 'doctor__user__email')
    list_filter = ('doctor', 'date', 'patient')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'name', 'date', 'time_from', 'time_to', 'comment',)
    search_fields = ('name', 'patient__last_name', 'doctor__user__email')
    list_filter = ('doctor', 'date', 'patient')


@admin.register(Anamesis)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'name', 'description',)
    search_fields = ('name', 'doctor__user__email')
    list_filter = ('doctor', 'name')
