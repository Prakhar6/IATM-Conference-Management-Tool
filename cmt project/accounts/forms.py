from django import forms
from .models import CustomUser
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class login_form(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # useful if needed later
        super().__init__(*args, **kwargs)

        # Crispy helper for layout
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Login', css_class='btn-dark w-100'))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid email or password.")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

    

class register_form(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'country', 'organization', 'phone', 'occupation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class='btn btn-primary w-100'))

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        cpw = cleaned_data.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', "Passwords do not match.")