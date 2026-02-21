from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
import asyncio
from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.contrib import messages
import secrets
from django.utils import timezone
from datetime import datetime
#models
from .models import Folder,Profile,Files,Storage
#Form
from .forms import Img_upload,FormFeild,MultipleFile
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import re
import math
import os
import shutil
from Drive.settings import BASE_DIR
from django.core.exceptions import ValidationError
from django.db import transaction

import sys
# Create your views here.

async def Home(request):
    pram={}
    User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()

    if User_loged_in:
        User_=request.user
        pram["User"]=User_
        folder=await print_folder_names(User_)
        pram['Folders']=folder
        pram['profile']=await profile_func(request.user)

    
    pram['loged_in']=User_loged_in
    

    return render(request,'Main/Main.html',pram)

@login_required(login_url=reverse_lazy('Home'))
async def profile(request):
    pram={}
    User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()
    
    
    if User_loged_in:
      User_=request.user
      pram["User"]=User_
    
    storage,_=await Storage.objects.aget_or_create(user=pram["User"])

    pram["Total_Storage"]=storage.Total_Storage/1024**3
    pram["User_Storage"]=round(storage.User_Storage/1024**3,2)
    print(float(pram["User_Storage"]))

    pram['loged_in']=User_loged_in
    Img_Form=Img_upload()
    pram['Img']=Img_Form

    profile = await Profile.objects.filter(user=request.user).afirst()
    
    pram['profile']=profile
   
    if request.method=='POST':
        Img_Form=Img_upload(request.POST,request.FILES)
        if Img_Form.is_valid():
          img_=Img_Form.cleaned_data['img_']
          img,created=await Profile.objects.aget_or_create(user=request.user,defaults={'img': img_})

          if not created:
              img.img = img_
              await img.asave()
          Img_form=Img_upload()
          pram['Img']=Img_form

          return render(request,'Main/Profile.html',pram)
        
    return render(request,'Main/Profile.html',pram)

@login_required(login_url=reverse_lazy('Home'))
async def Create_File(request):
   try:
     pram={}
     User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()
     pram['profile']=await profile_func(request.user)
     if User_loged_in:
         User_=request.user
         pram["User"]=User_
    
     pram['loged_in']=User_loged_in

     if request.method=='POST':
        Name=request.POST.get("Folder_Name")

        File=await Folder.objects.acreate(user=pram["User"],name=Name)
        return redirect("Home")
    
   except IntegrityError:
        messages.error(request, "Folder With Same Name Can Not Be Created")
   return render(request,"Main/Create.html",pram)


@login_required(login_url=reverse_lazy('Home'))
async def Files_(request,id):
    pram={}
    
    profile_=await profile_func(request.user)
    if profile_:
     pram['profile']=profile_
    User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()
    
    if User_loged_in:
      User_=request.user
      pram["User"]=User_
    
    pram['loged_in']=User_loged_in

    folder_=await Folder.objects.prefetch_related('Files').aget(user=request.user,id=id)
    
    pram['id']=id
    print(id)
    
    Files_in_current_Folder=await Files_names(folder_)
    print(Files_in_current_Folder)

    FileFeild_=FormFeild()
    
    storage,_=await Storage.objects.aget_or_create(user=pram["User"])
    Total_Storage=storage.Total_Storage
    User_Storage=storage.User_Storage
    if request.method=='POST':
        FileFeild_=FormFeild(request.POST,request.FILES)
        file_=request.FILES['File']
        token = secrets.token_urlsafe(32)

        if FileFeild_.is_valid():
          if Total_Storage>User_Storage+file_.size: 
              extension = file_.name.split(".")[-1]
              name_lis=file_.name.split(".")[0:-1]
              name_=""
              for i in name_lis: # This will cuz a a delay if a long length name is added to the file which may cuz DOS attack (sol: limit user file name)
                 name_+=i
              file_size=file_.size/1024**3
              Upload_File=Files(folder=folder_,image=file_,link_name=token,size=file_size,extension=extension,name=name_)
              await Upload_File.asave()
              storage.User_Storage=storage.User_Storage+int(file_.size)
              await storage.asave()
              return redirect('Files', id)
          else:
             messages.add_message(request,999,"No Storage Left",extra_tags="Storage_Full")
       
    else:
        FileFeild_=FormFeild()
                
    pram['form']=FileFeild_
    pram['Files']=Files_in_current_Folder
    pram['Absolute_url']=request.build_absolute_uri(reverse_lazy('Home'))
    
    return render(request,"Main/File.html",pram)

@login_required(login_url=reverse_lazy('Home'))
async def Multiple_Upload(request,id):
   User_is_login=await sync_to_async(lambda : request.user.is_authenticated)()
   pram={}

   profile_=await profile_func(request.user)

   if profile_:
     pram['profile']=profile_
    
   if User_is_login:
      User_=request.user
      print(User_)
      pram['User']=User_
      pram['loged_in']=User_is_login 

      
   return render(request,'Main/Multiple_file.html',pram)

@login_required(login_url=reverse_lazy('Home'))
async def Date(request,id):
    if request.method == 'POST':
        pram={}
    
        profile_=await profile_func(request.user)
        if profile_:
          pram['profile']=profile_

        User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()
    
        if User_loged_in:
          User_=request.user
          pram["User"]=User_
    
          pram['loged_in']=User_loged_in

        date1_str = request.POST.get("Date")
        date2_str = request.POST.get("Date_2")
        
        date1 = timezone.make_aware(datetime.strptime(date1_str, "%Y-%m-%dT%H:%M"))
        date2 = timezone.make_aware(datetime.strptime(date2_str, "%Y-%m-%dT%H:%M"))
       
        Folder_=await Folder.objects.aget(id=id)
        Files_=Folder_.Files.all()

        Files_List=[]

        async for i in Files_.aiterator():
          file_time = timezone.localtime(i.date)

          if date1<=file_time<=date2:
              Files_List.append(i)
        
        pram["Files"]=Files_List
        pram["id"]=id
        
        return render(request,"Main/Date.html",pram)

    raise Http404

@login_required(login_url=reverse_lazy('Home'))
async def Search(request):
   pram={}
   profile_=await profile_func(request.user)
   if profile_:
     pram['profile']=profile_

   User_loged_in=await sync_to_async(lambda : request.user.is_authenticated)()
    
   if User_loged_in:
     User_=request.user
     pram["User"]=User_
    
     pram['loged_in']=User_loged_in

   if request.method=='POST':
      val=request.POST.get('query')
      queryset=await sync_to_async(lambda : Files.objects.select_related('folder').filter(name__contains=val,folder__user=request.user))()
      
   pram['query_']=await sync_to_async(list)(queryset)
   print(pram['query_'])

   return render(request,"Main/Search.html",pram)


@login_required(login_url=reverse_lazy('Home'))
async def Multiple_Upload(request,id):

   User_is_login=await sync_to_async(lambda : request.user.is_authenticated)()
   pram={}

   profile_=await profile_func(request.user)

   if profile_:
     pram['profile']=profile_
    
   if User_is_login:
      User_=request.user
      print(User_)
      pram['User']=User_
      pram['loged_in']=User_is_login 
   
   folder_=await Folder.objects.prefetch_related('Files').aget(user=request.user,id=id)
   form = MultipleFile(request.POST, request.FILES)
   storage,_=await Storage.objects.aget_or_create(user=pram["User"])
   
   if request.method=='POST':
     
     flag=await mulupload(request,storage,folder_,id)
     if flag:
      return redirect("Files",id)

   pram['form']= form
   pram['id']=id
   return render(request, "Main/Multiple_file.html", pram)

 
@login_required(login_url=reverse_lazy('Home'))
def Download(request,id):
   img_= Files.objects.get(id=id,folder__user=request.user)
   folder=img_.folder
   if request.user==folder.user:
     file_path=img_.image.path
     name=img_.image.name.split("/")[-1]
     response = FileResponse(open(file_path, 'rb'))
     response['Content-Type'] = 'application/octet-stream'
     response['Content-Disposition'] = f'attachment; filename="{name}"'
     return response
   raise Http404

# All Del Functions

@login_required(login_url=reverse_lazy('Home'))
async def Remove(request,id):
    
    folder=await Folder.objects.prefetch_related('Files').aget(user=request.user,id=id)
    storage=await Storage.objects.aget(user=request.user)
    files=await Files_names(folder)

    total_file_size=0
    
    for file in files:
       total_file_size+=file.size*1024**3
    
    print(total_file_size)
    storage.User_Storage=storage.User_Storage-total_file_size
    await rmFile(files)
    await storage.asave()
    await folder.adelete()
    return redirect('Home')

@login_required(login_url=reverse_lazy('Home'))
async def Remove_Profile(request):

    if request.method=='POST':
        pfp=await Profile.objects.aget(user=request.user)
        await pfp.adelete()
    return await sync_to_async(redirect)('Profile')   
    
@login_required(login_url=reverse_lazy('Home'))
async def Remove_File(request,id,f_id): 
    
    folder= await sync_to_async(lambda : Folder.objects.filter(id=f_id,user=request.user).prefetch_related('Files').first())()
    File=await folder.Files.aget(id=id)
    storage=await Storage.objects.aget(user=request.user)
    size=File.size*1024**3
    storage.User_Storage=storage.User_Storage-size
   
    await rmFile([File])

    await storage.asave()
    await File.adelete()

    return redirect('Files', f_id)

#utlity Funtions

@sync_to_async
def print_folder_names(user):
    lis=[]
    for folder in user.Folders.all():
        lis.append(folder)
    return lis

@sync_to_async
def profile_func(user):
    profile =  Profile.objects.filter(user=user).first()
    return profile

@sync_to_async
def Files_names(Folder):
    lis=[]
    for file in Folder.Files.all():
        lis.append(file)
    return lis

@sync_to_async
def rmFile(Files):
   for File in Files:
      os.remove(File.image.path) 

@sync_to_async
def mulupload(request,storage,folder_,id):
 try:  
   Total_Storage=storage.Total_Storage
   User_Storage=storage.User_Storage
   name_=""
   Files_ = request.FILES.getlist('Files')
   with transaction.atomic(): # if error occurs roll back all files upload
        for file in Files_: #(O(n^2) algo )
          if  Total_Storage>User_Storage+file.size: 
            extension = file.name.split(".")[-1]
            name_lis=file.name.split(".")[0:-1]

            size=file.size # size of file in bytes
            for i in name_lis: # This will cuz a a delay if a long length name is added to the file which may cuz DOS attack (sol: limit user file name)
                name_+=i

            # Can not add multiple file validator in valiadtor so i added it here ofc there are better ways but rn now this have to do 
            valid_extensions = ('.jpg', '.jpeg', '.png', '.pdf','.pptx',".txt",".zip",".PDF")

            if size > 52428800:                
                messages.add_message(request,999,"File size too large to upload",extra_tags="Storage_full") # reusing message tag
                raise ValidationError("To large file")

            if not file.name.endswith(valid_extensions):               
               messages.add_message(request,999,"Invalid file type",extra_tags="Storage_full")# reusing message tag
               raise ValidationError("Invalid file type")
               

            token = secrets.token_urlsafe(32) 
            file_size=size/1024**3 # size of file in Mb
            Upload_File=Files(folder=folder_,image=file,link_name=token,size=file_size,extension=extension,name=name_)
            Upload_File.save()
            storage.User_Storage=storage.User_Storage+int(file.size)
            storage.save()
            User_Storage=storage.User_Storage
            name_=""

          else:
             messages.add_message(request,999,"Can not add any more Files Storage is Full",extra_tags="Storage_full")
             raise ValidationError("Storage full")
          
        return True
               
 except  ValidationError as e:
    return False
    
#This is multiple file upload