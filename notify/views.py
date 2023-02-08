from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
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
    #Checks for the logged in user
    logged_in = User.objects.get(id=request.user.id)

    #If the logged in user is admin then display all the notifications and order by the date sent.
    if logged_in.is_staff == True:
        notifications = Notification.objects.order_by('-send_at')

    #If it is not admin display notifications for that specific user
    else:
        notifications = Notification.objects.order_by('-send_at').filter(receiver=request.user)

    #Check for the status of notification for a specific user, the logged in user, and count the notifications that are unread
    notification_status = NotificationStatus.objects.filter(status='unread', user=request.user)
    number_of_unread_notifications = len(notification_status)

    #Check for the notification ids of the notifications that are unread
    notids = []
    for notid in notification_status.values():
        notids.append(notid['notification_id'])
    
    #Filter out the unread ones so that they can be displayed as the unread notifications.
    unread_notifications = Notification.objects.filter(id__in=notids)

    context = {
        "notifications": notifications,
        "unread_notifications": unread_notifications,
        "number_of_notifications": number_of_unread_notifications
    }

    return render(request, 'home.html', context)


@login_required(login_url='/')
def notifications(request):
    logged_in = User.objects.get(id=request.user.id)

    if logged_in.is_staff == True:
        notifications = Notification.objects.order_by('-send_at')

    else:
        notifications = Notification.objects.order_by('-send_at').filter(receiver=request.user)

    notification_status = NotificationStatus.objects.filter(status='unread', user=request.user)
    number_of_notifications = len(notification_status)

    notids = []
    for notid in notification_status.values():
        notids.append(notid['notification_id'])
    

    unread_notifications = Notification.objects.filter(id__in=notids)

    context = {
        "notifications": notifications,
        "unread_notifications": unread_notifications,
        "number_of_notifications": number_of_notifications,
        "notification_status": notification_status
    }
    return render(request, 'notifications/notifications.html', context)



@login_required(login_url='/')
@staff_member_required
def add_notification(request):
    users = User.objects.all()

    if request.method == 'POST':
        #Creating Notification and Notification Status at the same time.
        with transaction.atomic():
            sender = request.user
            message = request.POST['message']
            receiver_usernames = request.POST.getlist('receiver')

            #print(receiver_usernames)

            #List of notifications receivers
            receivers = []
            #If the selected receivers is all, then send message to every user
            if receiver_usernames == ['all']:
                users = User.objects.all()

                for user in users:
                    receiver = user
                    receivers.append(receiver)
            
            #If the selected receivers is customers, then send message to every user with a usertype of customer
            elif receiver_usernames == ['customers']:
                customers = User.objects.filter(user_type='customer')

                for customer in customers:
                    receiver = customer
                    receivers.append(receiver)

            #If the selected receivers is cashiers, then send message to every user with a usertype of cashier
            elif receiver_usernames == ['cashiers']:
                employees = User.objects.filter(user_type='cashier')

                for employee in employees:
                    receiver = employee
                    receivers.append(receiver)

            #Send notification to the specific selected individuals
            else:
                for receiver_username in receiver_usernames:
                    receiver = User.objects.get(username=receiver_username)
                    #print(receiver)
                    receivers.append(receiver)  
            
            #print(receiver)
            #Create Notification instance using the sender as the logged in user and the message.
            notification = Notification.objects.create(sender=sender, message=message)
            notification.receiver.set(receivers)

            #Create Notification status instance using the notification that was just created and the receivers in the receivers list.
            for receiver_users in receivers:
                notification_status = NotificationStatus.objects.create(notification=notification, user=receiver_users)
                notification_status.save()

            notification.save()

        return redirect('home')

    notification_status = NotificationStatus.objects.filter(status='unread', user=request.user)
    number_of_notifications = len(notification_status)

    context = {
        "users": users,
        "number_of_notifications": number_of_notifications
    }

    return render(request, 'notifications/create_notification.html', context)


@login_required(login_url='/')
def notification_detail(request, id):
    notification = Notification.objects.get(id=id)
    notification_status = NotificationStatus.objects.get(notification=notification, user=request.user)

    #Updating notification status to read once it's details is viewed
    notification_status.status = 'read'
    notification_status.save()

    logged_in = User.objects.get(id=request.user.id)

    if logged_in.is_staff == True:
        notifications = Notification.objects.order_by('-send_at')

    else:
        notifications = Notification.objects.order_by('-send_at').filter(receiver=request.user)

    
    number_of_unread = NotificationStatus.objects.filter(status='unread', user=request.user)
    number_of_notifications = len(number_of_unread)

    notids = []
    for notid in number_of_unread.values():
        notids.append(notid['notification_id'])
    

    unread_notifications = Notification.objects.filter(id__in=notids)
    
    context = {
        "notification": notification,
        "notifications": notifications,
        "unread_notifications": unread_notifications,
        "number_of_notifications": number_of_notifications
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
