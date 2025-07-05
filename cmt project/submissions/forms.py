from django import forms
from .models import Submissions
from accounts.models import CustomUser

class SubmissionForm(forms.ModelForm):
    paper_title = forms.CharField(max_length=255)
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False
    )
    co_authors = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    #add track and abstract

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

    class Meta:
        model = Submissions
        fields = ['paper_title', 'file', 'co_authors']

