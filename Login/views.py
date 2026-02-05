from django.shortcuts import render,redirect
from django.contrib.auth.models import User
import asyncio
from django.db.models import Q
from django.contrib.auth import authenticate,alogin ,logout
from django.contrib import messages
import re
from asgiref.sync import sync_to_async
import secrets
import string
import time
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import Http404

from django.urls import reverse_lazy
# Create your views here.

async def Send_Code(req,Email,Name,Pass):
    random_string = await sync_to_async(lambda:''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)))()
    await sync_to_async(lambda: req.session.__setitem__('signup_temp', {
        'Email': Email,
        'Name': Name,
        'Password': Pass,
        'Code': random_string,
        'By_Pass':True,
        'Expires': time.time() + 300  # expires in 5 minutes
    }))()

    subject, from_email, to = "You'r Drive Code is:", 'subhyoyogg@gmail.com',f'{Email}'
    random_string_=random_string

    html_content = render_to_string('Login/mail_template.html', {'Code':random_string_}) 
    text_content = strip_tags(html_content) 

    # create the email, and attach the HTML version as well.
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    await sync_to_async(req.session.save)()

    return True

async def Login(request):
    if request.method=='POST':
        Name_Email=request.POST.get("email")
        
        Password=request.POST.get("password")
        
        try:
            if Name_Email.endswith('@gmail.com'):
                await User.objects.aget(email=Name_Email)
                
            else:
                await User.objects.aget(username=Name_Email)

            user=await sync_to_async(authenticate)(request,username=Name_Email,password=Password)
            print(user,"User")
            if not user is None :
                await alogin(request,user)
                return redirect('Home')
            
            return render(request,'Login/Login.html',{'wpmessage':"Worng Password "})
            
        except:
            messages.error(request, "User by this Name or Email is Not presernt")

    return render(request,'Login/Login.html')

async def Register(request):
    if request.method=='POST':

      try:
        User_Name=request.POST.get('name')
        Email=request.POST.get('email')
        Password=request.POST.get('password')
       
        if not User_Name is None:
            user_=await User.objects.filter(Q(username=User_Name)).aexists()
            if user_:
             messages.add_message(request,999,'User Already Exists',extra_tags='User_name_exsits')
             raise ValueError('Presernt')

        if not Email is None:
            user_Email= await User.objects.filter(Q(email=Email)).aexists()
            if user_Email:
                messages.add_message(request,999,'Email Already in User',extra_tags='User_Email_exsits')
                raise ValueError('Presernt')

        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if len(Password)<8 or bool(re.search(r'\d',Password))==False or regex.search(Password)==None:
            messages.add_message(request,999,'Password Has to be >8 length and Contain Number and Special Character',extra_tags="User_Password")
            raise ValueError('Bad Pass')
        
        if_code_sended=await Send_Code(request,Email,User_Name,Password)

        if if_code_sended:
         return redirect('code')
        
      except ValueError:
         pass
    return render(request,'Login/Register.html')

async def code(request):
  tem=await sync_to_async(request.session.get)('signup_temp')
  pram={} 
  if(tem is not None):       
    if time.time()<tem['Expires']:
     code_=request.POST.get('code',None)
     if code_ is not None:
        code_=code_.strip()
        if tem['Code']==code_:
           new_temp=tem
           await sync_to_async(lambda : request.session.flush)()
           u=User(username=new_temp['Name'],email=new_temp['Email'])
           u.set_password(new_temp['Password'])
           await u.asave()
           await alogin(request,u,backend='django.contrib.auth.backends.ModelBackend')
           return redirect('Home')

    else:
     messages.add_message(request,999,'Code Has Been Expired',extra_tags="Code_resend_msg")
     pram={'code_exp':True}
    return render(request,'Login/code.html',pram)
  return HttpResponse('Not Allowed')

async def Resend(request):
    if request.method=='POST':
     random_string = await sync_to_async(lambda:''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)))()

     tem=await sync_to_async(lambda: request.session.__getitem__('signup_temp'))()
     tem['Code']=random_string
     tem['Expires']=time.time()+300
     subject, from_email, to = "You'r Resended Drive Code is:", 'subhyoyogg@gmail.com',f'{tem['Email']}'
     random_string_=random_string
   
     html_content = render_to_string('Login/mail_template.html', {'Code':random_string_}) 
     text_content = strip_tags(html_content) 

    # create the email, and attach the HTML version as well.
     msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
     msg.attach_alternative(html_content, "text/html")
     msg.send()
     await sync_to_async(request.session.save)()
     return HttpResponse('''
     <div class="col-md-12 text-center" id="msg"
     style="
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin-top: 20px;
        ">
        <p style="margin: 0;">Code has been resent successfully!</p>
        </div>
        
        <script>
    setTimeout(function () {
        var msg = document.getElementById("msg");
        msg.style.opacity = "0";
        setTimeout(function () {
            msg.style.display = "none";
        }, 500);
    }, 3000);
      </script>
        ''')
    raise Http404

async def Forget_Password(request):
    if   await sync_to_async(lambda :request.user.is_authenticated)():
     
     return redirect("Home")

    if request.method == "POST":
        try:
            email_or_name = request.POST.get("Email_Name")

            if email_or_name.endswith("@gmail.com"):
                user = await User.objects.aget(email=email_or_name)
            else:
                user = await User.objects.aget(username=email_or_name)

            
            token = secrets.token_urlsafe(32)

            
            request.session["forgot_password"] = {
                "user_id": user.id,
                "token": token,
                "Expire":time.time()+300
            }
            request.session.modified = True

           
            subject = "Your Drive Code"
            from_email = "subhyoyogg@gmail.com"
            to = user.email
            link=request.build_absolute_uri(reverse_lazy('reset',kwargs={"uid":user.id,"token":token}))
            html_content = render_to_string(
                "Login/forg.html",
                {"token": token,"link":link}
            )
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            return HttpResponse(
                "<div class='alert alert-success'>"
                "A link has been sent to your email"
                "</div>"
            )

        except User.DoesNotExist:
            messages.error(
                request,
                "User with Email/Username is not registered"
            )
            return render(
                request,
                "Login/partials/forget.html"
            )
           
    return render(request, "Login/Forget_pass.html")

async def Reset_Pass(request,uid,token):
   
   temp=await sync_to_async(request.session.get)("forgot_password")
   if temp==None:
     raise Http404
   if  await sync_to_async(lambda :request.user.is_authenticated)():
     return redirect("Home")
  
   id=await sync_to_async(request.session.get)("forgot_password")
  
   if not id['user_id']==uid or not id['token']==token:
     return redirect("Home")
  
   if time.time()>id["Expire"]:
     del request.session["forgot_password"]
     return HttpResponse("Time Has expired")
  
   New_pass=request.POST.get('New_Pass')
   if New_pass is not None:
     user=await User.objects.aget(id=uid)
     regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
     if len(New_pass)<8 or bool(re.search(r'\d',New_pass))==False or regex.search(New_pass)==None:
            messages.add_message(request,999,'Password Has to be >8 length and Contain Number and Special Character',extra_tags="ResetUser_Password")
            raise ValueError('Bad Pass')
     user.set_password(New_pass)    
     await user.asave()
   
     del request.session["forgot_password"]
     messages.success(request, "Pass Word Change sucussfuly")
     return redirect('Home')
     
   return render(request,"Login/resetpass.html",{"uid":uid,"token":token})
  
async def Logout(request):
    await sync_to_async(lambda : request.session.flush)()
    await sync_to_async(logout)(request)
    return redirect('Home')