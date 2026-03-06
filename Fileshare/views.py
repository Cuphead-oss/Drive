from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from Main.models import Files
from Main.views import profile_func
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import FileResponse,Http404
from .models import ShareFile

async def Fileshare(request,token):
    pram={}

    User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()

    if User_loged_in:
        User_=request.user
        pram["User"]=User_
        pram['profile']=await profile_func(request.user)

    pram['loged_in']=User_loged_in
    
    pram['file']=await Files.objects.filter(link_name=token).afirst()
    pram['token']=token
    
    return render(request,"Fileshare/Main.html",pram)

def Share_Download(request,token):
   img_= Files.objects.get(link_name=token)
   file_path=img_.image.path
   name=img_.image.name.split("/")[-1]
   response = FileResponse(open(file_path, 'rb'))
   response['Content-Type'] = 'application/octet-stream'
   response['Content-Disposition'] = f'attachment; filename="{name}"'
   return response
