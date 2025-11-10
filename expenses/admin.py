from django.contrib import admin
from .models import Group, GroupMember, Expense, ExpenseShare, Payment

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'email', 'phone', 'added_at']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'amount', 'currency', 'paid_by', 'created_at']

@admin.register(ExpenseShare)
class ExpenseShareAdmin(admin.ModelAdmin):
    list_display = ['expense', 'participant', 'amount_owed']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['expense', 'paid_by', 'paid_to', 'amount', 'paid_at']
