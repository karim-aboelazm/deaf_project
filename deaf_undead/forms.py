from django                     import forms
from .models                    import *
from django.contrib.auth.models import User

class NewUserRegister(forms.ModelForm):
    username    = forms.CharField(widget=forms.TextInput())
    email       = forms.EmailField(widget=forms.TextInput())
    password    = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model   = NewUser
        fields  =[
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'user_type'
        ]
    def clean_username(self):
        user_name   = self.cleaned_data["username"]
        if User.objects.filter(username=user_name).exists():
            raise forms.ValidationError("User With this account is already exists.")
        return user_name

class NewUserLogin(forms.Form):
    username                = forms.CharField(widget=forms.TextInput())
    password                = forms.CharField(widget=forms.PasswordInput()) 
    def clean_username(self):
        user_name           = self.cleaned_data.get("username")
        user_login_user_name= User.objects.filter(username=user_name)
        if user_login_user_name.exists():
            pass
        else:
            raise forms.ValidationError("User With this account is not exists.")
        return user_name

class UpdateNewUserProfile(forms.ModelForm):
    class Meta:
        model   = NewUser
        fields  = [
            "first_name",
            "last_name",
            "email",
            "profile",
        ]

class NewUserForgetPasswordForm(forms.Form):
    email       = forms.CharField(widget=forms.EmailInput(attrs={"placeholder":"Enter your email .."}))
    
    def clean_email(self):
        email   = self.cleaned_data["email"]
        if NewUser.objects.filter(user__email = email).exists():
            pass
        else:
            raise forms.ValidationError("User with this email does not exists .. ")
        return email

class NewUserResetPasswordForm(forms.Form):
    new_password                = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"New password"}))
    new_password_confirmation   = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm new password"})) 
    
    def clean_confirm_new_password(self):
        new_pass                = self.cleaned_data["new_password"]
        con_new_pass            = self.cleaned_data["new_password_confirmation"]
        if new_pass             != con_new_pass:
            raise forms.ValidationError("Passwords not matching..")
        return con_new_pass
    
    