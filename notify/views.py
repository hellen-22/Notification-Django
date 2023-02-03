from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as user_login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import UpdateView


from .forms import *
from .models import *

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                return redirect('login')
        else:
            messages.info('Passwords do not match')
            return redirect('register')

    else:
        return render(request, 'accounts/register.html')

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                user_login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")

    form = AuthenticationForm()

    return render(request, "accounts/login.html", context={"login_form":form})



@login_required(login_url='/')
def home(request):
    notifications = Notification.objects.all()
    number_of_notifications = len(notifications)

    context = {
        "notifications": notifications,
        "number_of_notifications": number_of_notifications
    }

    return render(request, 'home.html', context)


@login_required(login_url='/')
def notifications(request):
    notifications = Notification.objects.all().order_by('-send_at')
    number_of_notifications = len(notifications)

    print(number_of_notifications)

    context = {
        "notifications": notifications,
        "number_of_notifications": number_of_notifications
    }
    return render(request, 'notifications/notifications.html', context)



@login_required(login_url='/')
@staff_member_required
def add_notification(request):
    users = User.objects.all()

    if request.method == 'POST':
        sender = request.user
        message = request.POST['message']

        Notification.objects.create(sender=sender, message=message)
        return redirect('home')

    return render(request, 'notifications/create_notification.html')


@login_required(login_url='/')
def notification_detail(request, id):
    notification = Notification.objects.get(id=id)
    notifications = Notification.objects.all()
    context = {
        "notification": notification,
        "notifications": notifications
    }
    return render(request, "notifications/notification_detail.html", context)


class NotificationUpdate(UpdateView):
    model = Notification
    fields = ['message']
    template_name = 'notifications/update_notification.html'


@login_required(login_url='/')
@staff_member_required
def delete_notification(request, pk):
    notification = Notification.objects.get(id=pk)
    notification.delete()

    return redirect('notifications')
