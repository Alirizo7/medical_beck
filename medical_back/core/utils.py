import random
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code(length=6):
    """Generate a random verification code."""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(email, code):
    subject = "Your Verification Code"
    message = f"Use this code to verify your email: {code}"
    from_email = 'alirizok82@gmail.com'

    print(f"Sending email from: {from_email}")

    try:
        send_mail(subject, message, from_email, [email])
        return True
    except Exception as e:
        print(f"Error sending email to {email}: {e}")
        return False
