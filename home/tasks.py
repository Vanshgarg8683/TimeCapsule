from celery import shared_task
# from django.core.mail import send_mail    # we use send_mail if we only wanna send plain text
from django.core.mail import EmailMessage   # we use EmailMessage instead of send_mail so that we can send file also
from django.conf import settings
from django.utils import timezone as tz
import pytz
from .models import *
@shared_task
def send_email_to_user(subject, message, email, file_path=None, id=None):
    # send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
    
    capsule = TimeCapsule.objects.get(id=id)
    
    # it helps if updated capsule has later time as compare to old capsule
    if tz.now().astimezone(pytz.utc) < capsule.send_at:
        return
    
    if capsule.is_sent or capsule.is_deleted:
        return
    
    email=EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
    
    if file_path:
        # mimetype tells about the type of file that user attaching to the email so, django will automattically guess the type of file that user is giving if we set mimetype=None
        email.attach_file(file_path, mimetype=None)
        
    email.send()
    
    capsule.is_sent = True
    capsule.save()
