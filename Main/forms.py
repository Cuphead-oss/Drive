from django import forms
from . import validator

class Img_upload(forms.Form):
    img_=forms.ImageField(validators=[validator.File_is_Valid])

class FormFeild(forms.Form):
    File=forms.FileField(validators=[validator.File_is_Valid])