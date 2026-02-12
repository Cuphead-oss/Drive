from django.urls import path
from . import views
urlpatterns = [
    path('',views.Home,name="Home"),
    path('Profile/',views.profile,name="Profile"),
    path('Create_File/',views.Create_File,name="Create_File"),
    path("Folder/Files/<int:id>/",views.Files_,name="Files"),
    path("Multiple_Upload/Files/<int:id>/",views.Multiple_Upload,name="Multiple_upload"),
    path("Download/<int:id>/",views.Download,name="Download"),
    path("Date/<int:id>/",views.Date,name="Date"),
    path("Search",views.Search,name="Search"),
    #Rm/Del Functions
    path('Remove_Profile',views.Remove_Profile,name="rm_profile"),
    path('Remove/<int:id>/',views.Remove,name="Remove"),
    path('Del/File/<int:id>/<int:f_id>/',views.Remove_File,name="Del_File")
]