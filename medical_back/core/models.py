from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    birth_date = models.DateField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'


class Patient(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    comment = models.TextField(blank=True, null=True)
    is_contact = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Medication(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Procedure(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='procedures')
    date = models.DateField()
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='procedures')

    def __str__(self):
        return self.name


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    name = models.CharField(max_length=100)
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.patient} ({self.date} {self.time_from}-{self.time_to})'

    class Meta:
        ordering = ['date', 'time_from']
