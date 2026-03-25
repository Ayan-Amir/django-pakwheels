from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
        }


class ProfileInfoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'phone_number', 'city')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
        }


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_picture',)


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current password'}),
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('New passwords do not match.')

        return cleaned_data
