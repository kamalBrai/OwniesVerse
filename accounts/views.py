from django.shortcuts import render,redirect
from datetime import datetime
from .models import CustomUserModel
import re
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from accounts.models import Order

from .models import Profile
from .forms import ProfileForm
# Create your views here.






def register(request):
    if request.method=='POST':
        fname=request.POST['first_name']
        lname=request.POST['last_name']
        uname=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password1=request.POST['password1']
        phone=request.POST['phone']
        street_address=request.POST['street_address']
        
        error=[]

        if password==password1:
            if CustomUserModel.objects.filter(username=uname).exists():
                error.append('username is already exists')
            
            if CustomUserModel.objects.filter(email=email).exists():
                error.append('Email is already exists')
                
            if re.search(r"/d",password):
                error.append('password must contain atleast one numeric value')

            

            try:
                validate_password(password)

                if not error:
                  CustomUserModel.objects.create_user(first_name=fname,last_name=lname,username=uname,email=email,password=password,phone=phone,street_address=street_address)
                  messages.success(request,'your account is successfully register')
                  return redirect('login')
                else:
                    for i in error:
                        messages.error(request,i)
                    return redirect('register')
            
            except ValidationError as e:
                for i in e.messages:
                    messages.error(request,i)
                return redirect('register')
            
        else:
            messages.error(request,'password and confirm password doesnot match')
            return redirect('register')

    return render(request,'account/register.html')

def log_in(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        remember_me=request.POST.get('remember_me')
        
        
        if not CustomUserModel.objects.filter(username=username).exists():
            messages.error(request,'username doesnot register yet')
            return redirect('login')
        
        user=authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            if remember_me:
                request.session.set_expiry(150000)
            else:
                request.session.set_expiry(0)

            next=request.POST.get('next','')
            return redirect(next if next else'index')
        else:
            messages.error(request,'password invalid')
            return redirect('login')

    next=request.GET.get('next','')   
    return render(request,'account/login.html',{'next':next})

def log_out(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('log_in')


'''
Profile Section
'''

@login_required(login_url="log_in")
def profile_dashboard(request):
    return render(request, 'profile/dashboard.html')


@login_required(login_url="log_in")
def profile(request):
    profile,created=Profile.objects.get_or_create(user=request.user)
    form=ProfileForm(instance=profile)

    if request.method == "POST":
        form=ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    context={
        'form':form
    }

    return render(request, 'profile/profile.html',context)

def my_order(request):
    if request.method == 'POST':
        phone=request.POST['phone']
        address=request.POST['address']
        cart=request.session.get('cart')
        print(cart)
        # {'5': {'userid': 4, 'product_id': 5, 'name': 'Fan', 'quantity': 3, 
        #        'price': '11400.00', 'image': '/media/images/android-chrome-192x192.png'}, 
        #        '1': {'userid': 4, 'product_id': 1, 'name': 'Miraj tamang', 'quantity': 1, 
        #              'price': '6000.00', 'image': '/media/images/shoes.jpeg'}} 
        for i in cart:
            product=cart[i]['name']
            quantity=cart[i]['quantity']
            price=cart[i]['price']
            total=float(price) * quantity
            image=cart[i]['image'] 
            order=Order(product=product,quantity=quantity,price=price,image=image,total=total,phone=phone,address=address,user=request.user)
            order.save()
        request.session['cart']={}
        return redirect('my_order')
         
         
    myorder=Order.objects.filter(user=request.user)
    context = {
        'myorder' : myorder
    }
    return render(request, 'profile/my_order.html', context)