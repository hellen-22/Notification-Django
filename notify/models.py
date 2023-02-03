from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return {self.message}

    def get_absolute_url(self):
        return reverse('notifications')
