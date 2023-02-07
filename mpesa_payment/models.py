from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Transaction(models.Model):
    phone_number = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now=True)
    checkout_request_id = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'Transaction for {self.phone_number}'