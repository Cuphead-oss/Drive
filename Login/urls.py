from django.urls import path
from . import views
urlpatterns = [
    path('',views.Login,name="Login"),
    path('/Register',views.Register,name="reg"),
    path('/Code',views.code,name='code'),
    path('/Resend',views.Resend,name="resend"),
    path('/Logout',views.Logout,name="logout"),
    path("/ForgetPass",views.Forget_Password,name="Forget"),
    path("/resetpass/<int:uid>/<str:token>/",views.Reset_Pass,name="reset")
]