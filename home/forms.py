from django import forms
from .models import TimeCapsule
from django.utils import timezone
from pytz import all_timezones

class TimeCapsuleForm(forms.ModelForm):

    class Meta:
        model = TimeCapsule
        fields = ['email', 'file', 'message', 'send_at']
        widgets = {
            'send_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }

    def clean_send_at(self):
        send_at = self.cleaned_data['send_at']
        if send_at and send_at < timezone.now():
            raise forms.ValidationError("Send time cannot be in the past.")
        return send_at
