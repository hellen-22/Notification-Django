from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, AbstractUser

USER_TYPE_CHOICES = (
    ('admin', 'admin'),
    ('customer', 'customer'),
    ('cashier', 'cashier')
)

NOTIFICATION_STATUS_CHOICES = (
    ('read', 'read'),
    ('unread', 'unread')
)
# Create your models here.


#Creating a custom user so as to ad the usertype field
class User(AbstractUser):
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=255, choices=USER_TYPE_CHOICES, default='customer')


    def __str__(self) -> str:
        return self.username

#Notification table to store notification
class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ManyToManyField(User, related_name='receiver')
    message = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.message)

    def get_absolute_url(self):
        return reverse('notifications')

#For storing notification of individual users and the status of their notification.
class NotificationStatus(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='notification')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=NOTIFICATION_STATUS_CHOICES, default='unread')

    def __str__(self) -> str:
        return f'Notification for {self.user.username}'