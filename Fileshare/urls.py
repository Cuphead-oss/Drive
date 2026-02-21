from django.urls import path
from . import views
urlpatterns = [
    path("",views.Fileshare,name="Fileshare"),
    path("Share_Download",views.Share_Download,name="Share_Download")
]