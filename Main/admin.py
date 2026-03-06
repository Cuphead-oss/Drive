from django.contrib import admin
from .models import Storage,Files,Profile,Folder
from django.contrib.auth.models import User
from django.db.models import F,FloatField,ExpressionWrapper
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse
import math
from django.db.models import Count
# Register your models here.


@admin.register(Storage)
class User_Storage(admin.ModelAdmin):
    list_display=["user","storage_user_in_gb"]
    
    @admin.display(ordering='User_Storage')
    def storage_user_in_gb(self,Storage):
        return abs(round(Storage.storage_user_in_gb,2))
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            storage_user_in_gb=ExpressionWrapper(F("User_Storage")/(1024.0**3),
            output_field=FloatField())
        )

@admin.register(Profile)
class Pfp(admin.ModelAdmin):
    list_display=["user","folder"]

    @admin.display(ordering="folder")
    def folder(self,pfp):
        url=reverse('admin:Main_folder_changelist')+'?'+urlencode(
            {
                'user__id':str(pfp.user.id)
            }
        )
        return format_html('<a href="{}">{}</a>',url,pfp.folder)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
         folder=Count(F("user__Folders"))
        )

admin.site.register(Folder)