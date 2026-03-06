from django import forms
from . import validator

class Img_upload(forms.Form):
    img_=forms.ImageField()

class FormFeild(forms.Form):
    File=forms.FileField()

class MultipleFile(forms.Form):
    Files=forms.FileField(widget=forms.TextInput(attrs={
            "name": "images",
            "type": "File",
            "class": "form-control",
            "multiple": True,
    }), label = "")
