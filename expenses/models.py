from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  
    email = models.EmailField(blank=True, null=True) 
    phone = models.CharField(max_length=20, blank=True, null=True)  
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'name')  

    def __str__(self):
        return f"{self.name} ({self.group.name})"

class Expense(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('INR', 'INR'),
        ('GBP', 'GBP'),
        ('JPY', 'JPY'),
    ]
    
    SPLIT_CHOICES = [
        ('equal', 'Equal Split'),
        ('unequal', 'Unequal Split'),
    ]
    
    PAYER_CHOICES = [
        ('single', 'Single Payer'),
        ('multiple', 'Multiple Payers'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    paid_by = models.ForeignKey(GroupMember, on_delete=models.CASCADE, null=True, blank=True)  
    split_type = models.CharField(max_length=10, choices=SPLIT_CHOICES, default='equal')
    payer_type = models.CharField(max_length=10, choices=PAYER_CHOICES, default='single')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency}"

class ExpensePayer(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='payers')
    payer = models.ForeignKey(GroupMember, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.payer.name} paid {self.amount_paid} for {self.expense.name}"

class ExpenseShare(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    participant = models.ForeignKey(GroupMember, on_delete=models.CASCADE) 
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)

class Payment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    paid_by = models.ForeignKey(GroupMember, related_name='payments_made', on_delete=models.CASCADE)
    paid_to = models.ForeignKey(GroupMember, related_name='payments_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)