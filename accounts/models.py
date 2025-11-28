from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUserModel(AbstractUser):
    phone=models.CharField(max_length=200)
    street_address=models.CharField(max_length=200)

class Profile(models.Model):
    user=models.OneToOneField(CustomUserModel, on_delete=models.CASCADE,related_name='profile')
    profile_picture=models.ImageField(upload_to="profile_picture")
    bio=models.TextField()
    dob=models.DateField(null=True)
    created_date=models.DateTimeField(auto_now=True)


class Order(models.Model):
    product=models.CharField(max_length=200)
    user=models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    phone=models.CharField(max_length=200)
    address=models.CharField(max_length=200)
    price=models.CharField(max_length=200)
    quantity=models.PositiveSmallIntegerField()
    total=models.CharField(max_length=200)
    is_pay=models.BooleanField(default=False)
    image=models.ImageField(upload_to="order_image")
    order_date=models.DateTimeField(auto_now=True)