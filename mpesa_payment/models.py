from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Transactions(models.Model):
    phone_number = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    received_at = models.DateTimeField(auto_now_add=True)
    checkout_request_id = models.CharField(max_length=255)
    merchant_request_id = models.CharField(max_length=255)
    mpesa_receipt_no = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.phone_number