from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import TimeCapsuleForm
from .tasks import *
from .models import *
def registration(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('/registration')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('/registration')

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        messages.success(request, 'Account has been created successfully')
        return redirect('/login')

    return render(request, 'registration.html')

def loginpage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Incorrect Username')
            return redirect('/login')

        user = authenticate(username=username, password=password)
        if not user:
            messages.error(request, 'Incorrect Credentials!')
            return redirect('/login')

        login(request, user)
        messages.success(request, 'You have logged in successfully!')
        return redirect('/capsule')

    return render(request, 'login.html')

def logoutpage(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('/login')

def home(request):
    return render(request, 'home.html')





#  django.utils and pytz both have timezone so it's safe to provide different name to their timezoneso that there is no problem occuring chances
from django.utils import timezone as tz
import pytz

@login_required
def create_capsule(request):
    if request.method == 'POST':
        form = TimeCapsuleForm(request.POST, request.FILES)
        if form.is_valid():
            capsule = form.save(commit=False)
            capsule.user = request.user

            #   IT WILL GIVE PROPERLY FORMATTED VALUE OF send_at
            send_at = form.cleaned_data['send_at']

            #  IT WILL CREATE OBJECT FOR IST(INDIAN STANDARD TIMEZONE), SO THAT WE CAN CONVERT DATETIMES TO IST
            kolkata_tz = pytz.timezone('Asia/Kolkata')
            
            # here we are checking the send_at datetime that was given by user has timezone info or not most of the time django doesn't have the timezone info still there are some chances that it's already have timezone info.
            if tz.is_naive(send_at): # Means No timezone info
                
                # Here this line signifies that we are converting given datatime into IST timezone
                aware_local = kolkata_tz.localize(send_at)
            else: # Means have timezone info. (very less chances)
                
                #  IF django already have timezone info and i am 100% sure that user is from india then there no point of converting IST TO IST ,   WE CAN SIMPLY SKIP THIS ELSE CONDITION
                aware_local = send_at.astimezone(kolkata_tz)

            # 3. Convert that IST time to UTC for Celery
            send_at_utc = aware_local.astimezone(pytz.utc)

            # 4. Save UTC into DB (optional—you can save aware_local if you prefer)
            capsule.send_at = send_at_utc
            capsule.save()

            # 5. Schedule the task
            file_path=None
            if capsule.file:
                file_path = capsule.file.path
            send_email_to_user.apply_async(
                args=["Your Time Capsule", capsule.message, capsule.email, file_path, capsule.id],
                eta=send_at_utc
            )

            messages.success(request, "Time Capsule Scheduled!")
            return redirect('/success')

    else:
        form = TimeCapsuleForm()

    return render(request, 'capsule.html', {'form': form})


@login_required
def my_capsules(request):
    capsules = TimeCapsule.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'mycapsules.html', {'capsules': capsules})

@login_required
def edit_capsule(request, id):
    capsule = TimeCapsule.objects.get(id=id, user=request.user)
    if tz.now().astimezone(pytz.utc) > capsule.send_at:
        messages.warning(request, 'The Capsule has alreasy been sent and cannot be edited.')
        return redirect('/mycapsules')
    
    if request.method == 'POST':
        form = TimeCapsuleForm(request.POST, request.FILES, instance=capsule)
        if form.is_valid():
            updated_capsule = form.save(commit=False)

            send_at = form.cleaned_data['send_at']
            kolkata_tz = pytz.timezone('Asia/Kolkata')
            if tz.is_naive(send_at):
                aware_local = kolkata_tz.localize(send_at)
            else:
                aware_local = send_at.astimezone(kolkata_tz)
            send_at_utc = aware_local.astimezone(pytz.utc)

            updated_capsule.send_at = send_at_utc
            updated_capsule.save()

            file_path=None
            if updated_capsule.file:
                file_path = updated_capsule.file.path
            send_email_to_user.apply_async(
                args=["Your Time Capsule", capsule.message, capsule.email, file_path, updated_capsule.id],
                eta=send_at_utc
            )
            messages.success(request, 'Capsule updated successfully!')
            return redirect('/mycapsules')
    else:
        form = TimeCapsuleForm(instance=capsule)

    return render(request, 'editcapsule.html', {'form': form})

@login_required
def delete_capsule(request, id):
    capsule = TimeCapsule.objects.get(id=id, user=request.user)
    capsule.is_deleted = True
    capsule.delete()
    messages.success(request, 'Capsule has been deleted successfully!!')
    return redirect('/mycapsules')
def successpage(request):
    return render(request, 'success.html')
