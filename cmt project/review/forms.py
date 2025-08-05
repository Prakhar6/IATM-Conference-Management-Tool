from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'recommendation']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'recommendation': forms.Select(attrs={'class': 'form-select'}),
        }
