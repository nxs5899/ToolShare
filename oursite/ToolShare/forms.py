from django.db import models
from django import forms
from django.forms import ModelForm
from ToolShare.models import Tool, Registrant, BorrowTool, Shed, BlackoutTool
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        #fields = '__all__'
        fields = ('name','description','instructions','tool_category','tool_location','tool_condition')


class ToolUpdate(forms.ModelForm):
    class Meta:
        model = Tool
        fields = '__all__'


class BorrowToolForm(forms.ModelForm):
    class Meta:
        model = BorrowTool
        fields = ("start_date","end_date","borrowerId","toolId","borrower_notes", "lender_notes")


class ReturnToolForm(forms.ModelForm):
    class Meta:
        model = BorrowTool
        fields = ("borrowerId", "toolId", "currently_borrowed", "return_date")



class RegistrantForm(forms.ModelForm):
    class Meta:
        model = Registrant
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)
       # del self.fields['username']


    class Meta:
        model = Registrant
        fields = ("email", 'first_name', 'last_name','telephone', 'address_line1', 'address_line2', 'date_of_birth','sharezone')



class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
      #  del self.fields['username']

    class Meta:
        model = Registrant
        # fields = '__all__'
        fields = ('first_name', 'last_name','telephone', 'address_line1', 'address_line2')

class Approve_Request(forms.ModelForm):
    class Meta:
        model = BorrowTool
        fields = ("borrowerId", "toolId", "start_date", "end_date")

class CustomUserLoginForm(AuthenticationForm):

    class Meta:
        model = Registrant
        fields = ("email","password")
    '''
    # email = forms.EmailField(required=True, label="Email", widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'email'}))
    password = forms.CharField(required=True, label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))
    '''

class CustomUserPasswordChange(PasswordChangeForm):
    class Meta:
        model = Registrant
        fields = '__all__'


class UpdateShedForm(forms.ModelForm):
    class Meta:
        model = Shed
        fields = ("description", "address", "name")


class AdminCreateForm(UserCreationForm):

    def __init__(self, *args, **kargs):
        super(AdminCreateForm, self).__init__(*args, **kargs)
       # del self.fields['username']

    class Meta:
        model = Registrant
        fields = ("email", 'first_name', 'last_name')

class BlackoutToolForm(forms.ModelForm):
    class Meta:
        model = BlackoutTool
        fields = ("start_date","end_date","toolId")