from django import forms
from .models import Submissions
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
    
    # Replace ModelMultipleChoiceField with a simple CharField for emails
    co_author_emails = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter co-author emails (one per line)'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file type
            allowed_types = ['pdf']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_types:
                raise forms.ValidationError("Please upload a PDF file")
            # Validate file size
            if file.size > 10*1024*1024:
                raise forms.ValidationError("File size must be less than 10MB")
        elif not self.instance.pk:
            # File is required for new submissions
            raise forms.ValidationError("Please upload a PDF file")
        return file

    def clean_co_author_emails(self):
        emails = self.cleaned_data.get('co_author_emails', '').strip()
        if not emails:
            return []
        
        email_list = [email.strip() for email in emails.split('\n') if email.strip()]
        co_authors = []
        invalid_emails = []
        
        for email in email_list:
            try:
                user = CustomUser.objects.get(email=email)
                co_authors.append(user)
            except CustomUser.DoesNotExist:
                invalid_emails.append(email)
        
        if invalid_emails:
            raise ValidationError(
                f"The following emails are not registered in the system: {', '.join(invalid_emails)}"
            )
        
        return co_authors

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Get co-authors from the cleaned data
            co_authors = self.cleaned_data.get('co_author_emails', [])
            # Clear existing co-authors and set new ones
            instance.co_authors.clear()
            if co_authors:
                instance.co_authors.add(*co_authors)
        return instance

    class Meta:
        model = Submissions
        fields = ['paper_title', 'file']

