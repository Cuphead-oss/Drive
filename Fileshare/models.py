from django.db import models
from django.contrib.auth.models import User
from Main.models import Files
# Create your models here.

class ShareFile(models.Model):
    shared_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name="Shared_by_usr")
    shared_to=models.ForeignKey(User,on_delete=models.CASCADE,related_name="Shared_to_usr")
    file=models.ForeignKey(Files,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["shared_to","file"]

