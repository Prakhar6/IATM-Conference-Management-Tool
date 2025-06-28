from django import forms
from .models import Role

class MembershipForm(forms.Form):
    role1 = forms.ChoiceField(
        choices=Role.choices,
        label="Select Role 1",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    role2 = forms.ChoiceField(
        choices=Role.choices,
        label="Select Role 2",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default value for role2 to "N/A" only on GET (unbound form)
        if not self.is_bound:
            self.fields['role2'].initial = Role.NA

    def clean(self):
        cleaned_data = super().clean()
        role1 = cleaned_data.get('role1')
        role2 = cleaned_data.get('role2')

        # Skip validation if role2 is 'N/A'
        if role2 == Role.NA:
            return cleaned_data

        if role1 == role2:
            raise forms.ValidationError("Please choose two different roles.")

        return cleaned_data
