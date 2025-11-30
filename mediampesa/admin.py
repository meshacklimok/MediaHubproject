from django.contrib import admin
from .models import Transactions

# Register your models here.
@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number', 'amount', 'status', 'date_created', 'mpesa_receipt_number')
    list_filter = ('status', 'date_created')
    search_fields = ('transaction_id', 'phone_number', 'mpesa_receipt_number', 'name', 'email')
