"""Account forms — candidate registration and profile."""
import re

from django import forms
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()

_PHONE_RE = re.compile(r'^\+?[\d\s\-()]{6,40}$')


class CandidateRegistrationForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Password (again)')
    phone = forms.CharField(
        max_length=40,
        help_text='Required for candidates.',
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not phone:
            raise forms.ValidationError('Phone number is required for candidates.')
        if not _PHONE_RE.match(phone):
            raise forms.ValidationError('Enter a valid phone number (digits; + allowed at start).')
        return phone

    def clean(self):
        data = super().clean()
        p1 = data.get('password1')
        p2 = data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return data


class CandidatePhoneForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not phone:
            raise forms.ValidationError('Phone number is required.')
        if not _PHONE_RE.match(phone):
            raise forms.ValidationError('Enter a valid phone number (digits; + allowed at start).')
        return phone
