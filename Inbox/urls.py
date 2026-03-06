from django.urls import path
from . import views
urlpatterns = [
    path("",views.Inbox,name="Inbox"),
    path("Download/<int:id>/",views.Shared_Download,name="Share_Download"),
    path("Shared_Remove/<int:id>/",views.Shared_Remove,name="Share_rm"),
]