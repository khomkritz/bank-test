from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=150, null=True)
    email = models.CharField(max_length=55, unique=True)
    password = models.CharField(max_length=200)
    tel = models.CharField(max_length=9, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class Bank(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class Account(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    bank_number = models.CharField(max_length=10, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class Transfer(models.Model):
    from_account = models.ForeignKey(Account, related_name='transfers_sent', on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, related_name='transfers_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class Token(models.Model):
    customer_id = models.IntegerField()
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)