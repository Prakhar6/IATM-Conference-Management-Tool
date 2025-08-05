from django import forms
from .models import Submissions, Track
from accounts.models import CustomUser
from django.core.exceptions import ValidationError

class SubmissionForm(forms.ModelForm):
    paper_title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )
    track = forms.ModelChoiceField(
        queryset=Track.objects.none(),  # Filtered in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    co_author_email_1 = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if none'}),
        label='Co-Author 1 Email'
    )
    co_author_email_2 = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if none'}),
        label='Co-Author 2 Email'
    )
    co_author_email_3 = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if none'}),
        label='Co-Author 3 Email'
    )

    def __init__(self, *args, conference=None, **kwargs):
        super().__init__(*args, **kwargs)
        if conference:
            self.fields['track'].queryset = Track.objects.filter(conference=conference)

        # Initialize co-author users to None
        self._co_author_users = [None, None, None]

        # Pre-fill emails for editing
        if self.instance.pk:
            self.fields['co_author_email_1'].initial = self.instance.co_author1.email if self.instance.co_author1 else ''
            self.fields['co_author_email_2'].initial = self.instance.co_author2.email if self.instance.co_author2 else ''
            self.fields['co_author_email_3'].initial = self.instance.co_author3.email if self.instance.co_author3 else ''

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise forms.ValidationError("Please upload a PDF file")
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB")
        elif not self.instance.pk:
            raise forms.ValidationError("Please upload a PDF file")
        return file

    def _validate_co_author_email(self, email):
        if not email:
            return None
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError(f"Email '{email}' is not registered.")

    def clean_co_author_email_1(self):
        email = self.cleaned_data.get('co_author_email_1')
        user = self._validate_co_author_email(email)
        self._co_author_users[0] = user
        return email or ''

    def clean_co_author_email_2(self):
        email = self.cleaned_data.get('co_author_email_2')
        user = self._validate_co_author_email(email)
        self._co_author_users[1] = user
        return email or ''

    def clean_co_author_email_3(self):
        email = self.cleaned_data.get('co_author_email_3')
        user = self._validate_co_author_email(email)
        self._co_author_users[2] = user
        return email or ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.status = Submissions.StatusChoices.PENDING

        # Explicitly assign co-authors from cleaned data
        instance.co_author1 = self._co_author_users[0]
        instance.co_author2 = self._co_author_users[1]
        instance.co_author3 = self._co_author_users[2]

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Submissions
        fields = ['paper_title', 'file', 'track', 'co_author_email_1', 'co_author_email_2', 'co_author_email_3']
