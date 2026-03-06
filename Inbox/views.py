
from django.shortcuts import render,redirect
from django.http import HttpResponse
from Main.models import Files
from Main.views import profile_func
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import FileResponse,Http404
from Fileshare.models import ShareFile
from django.contrib.auth.decorators import login_required


@login_required(login_url=reverse_lazy('Home'))
async def Inbox(request):

    pram={}
    User_=await sync_to_async(get_user)(request)

    if User_.is_authenticated:
        
        pram["User"]=User_
        pram['profile']=await profile_func(User_)
        pram['loged_in']=User_.is_authenticated

    Share_File=await sync_to_async(lambda : ShareFile.objects.select_related('shared_by','shared_to','file').filter(shared_to=pram['User']))()

    if not Share_File is None :
      pram["File_Shared_User"]=await sync_to_async(list)(Share_File)
    
    return render(request,"Inbox/Inbox.html",pram)

@login_required(login_url=reverse_lazy('Home'))
def Shared_Download(request,id):
   img_= ShareFile.objects.prefetch_related('file').get(file__id=id,shared_to=request.user)
   if request.user==img_.shared_to:
     file_path=img_.file.image.path
     name=img_.file.image.name.split("/")[-1]
     response = FileResponse(open(file_path, 'rb'))
     response['Content-Type'] = 'application/octet-stream'
     response['Content-Disposition'] = f'attachment; filename="{name}"'
     return response
   raise Http404

@login_required(login_url=reverse_lazy('Home'))
def Shared_Remove(request,id):
   img_= ShareFile.objects.prefetch_related('file').get(file__id=id,shared_to=request.user)
   if request.user==img_.shared_to:
      img_.delete()
      return redirect('Inbox')
   raise Http404
     