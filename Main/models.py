from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user=models.OneToOneField(User,related_name="User_profile_image",on_delete=models.CASCADE)
    img=models.ImageField(null=True,blank=True,upload_to="profile")

class Folder(models.Model):
    user=models.ForeignKey(User,related_name="Folders",on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    class Meta:
        unique_together = ["user", "name"]


class Files(models.Model):
    folder=models.ForeignKey(Folder,on_delete=models.CASCADE,related_name="Files")
    file=models.FileField(null=True,blank=True,upload_to="files")
    image=models.ImageField(null=True,blank=True,upload_to="images") # Rn I am Using This for All Files
    #Auto Generated
    link_name=models.CharField(max_length=100) 
    #Meta
    name=models.CharField(max_length=100)
    size=models.FloatField()
    date=models.DateTimeField(auto_now_add=True)
    extension=models.CharField(max_length=50)

class Storage(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    Total_Storage=models.BigIntegerField(default=5*1024**3)
    User_Storage=models.BigIntegerField(default=0)
