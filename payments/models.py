from django.db import models
from accounts.models import Order

# Create your models here.
class Transaction(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    user=models.CharField(max_length=200)
    transaction_id=models.CharField(max_length=200)
    total=models.CharField(max_length=200)
    payment_data=models.DateTimeField(auto_now=True)
