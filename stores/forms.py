from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from core.models import (
    User
)


class EmailSubscriberForm(forms.Form):
    """

    """
    first_name = forms.CharField(label="First name", required=False)
    email = forms.EmailField(label="Email")


class RegistrationForm(forms.Form):
    """

    """
    EMAIL_TAKEN_MSG = "There is already an account associated with that email address."

    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), min_length=5,
                                   label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(),
                                       min_length=5, label="Confirm Password")

    def add_store(self, store):
        self.store = store

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(customer_of=self.store, email=email).exists():
            raise forms.ValidationError(self.EMAIL_TAKEN_MSG)

        return email

    def clean(self):
        """
        Make sure that the new passwords match.
        """
        password = self.cleaned_data.get("password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input((Submit("submit", "Register")))


class PasswordResetForm(forms.Form):
    """
    Password reset form
    """
    email = forms.EmailField()

    def add_store(self, store):
        self.store = store

    def clean_email(self):
        """
        Make sure the email address is associated with an account.
        """
        error_string = "There is no account associated with that email address."
        email = self.cleaned_data["email"]

        try:
            User.objects.get(email=email, customer_of=self.store)
        except User.DoesNotExist:
            raise forms.ValidationError(error_string)

        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input((Submit("submit", "Send reset email")))


class SetPasswordForm(forms.Form):
    """
    Reset a password after clicking link in email.
    """
    new_password = forms.CharField(widget=forms.PasswordInput(), min_length=5,
                                   label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(),
                                       min_length=5, label="Confirm Password")

    def clean(self):
        """
        Make sure that the new passwords match.
        """
        new_password = self.cleaned_data.get("new_password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input((Submit("submit", "Reset password")))


class CheckoutForm(forms.Form):
    email = forms.EmailField(label="Email")
    confirm_email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")


class GetAccessForm(forms.Form):
    first_name = forms.CharField(label="First name")
    email = forms.EmailField(label="Email")
    marketing = forms.BooleanField(widget=forms.CheckboxInput)

