from django.db import models
from django.contrib.auth.models import User
from pytz import all_timezones

class TimeCapsule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    message = models.TextField()
    send_at = models.DateTimeField()  # Will be stored in UTC
    file = models.FileField(upload_to='capsule_uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sent = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"Capsule to {self.email} scheduled at {self.send_at}"
