from django.db import models
from django.conf import settings
# Create your models here.
class Transactions(models.Model):
    # transaction id : mpesa's valid transaction id for successfull payments 
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # mpesa receipt number 
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    # pending / complete 
    status = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True) # true date / time / apps perspective 
    date_created = models.DateTimeField(auto_now_add=True) # date of capture server perspective
    email = models.EmailField(blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    
    def __str__(self):
        return f"Transaction {self.mpesa_receipt_number or self.transaction_id} - {self.status}"
