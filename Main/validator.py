from django.core.exceptions import ValidationError
from . import models
from django.contrib.auth.models import User
def File_is_Valid(value):
    file_size=value.size  
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.pdf','.pptx',".txt",".zip")
    if file_size > 52428800:
        raise ValidationError("You cannot upload file more than 50Mb")
    elif not value.name.endswith(valid_extensions):
        raise ValidationError("You cannot upload this type of file ")
    else:
        return value