from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from decimal import Decimal
import json
from .models import Group, GroupMember, Expense, ExpenseShare, Payment, ExpensePayer
from .forms import CustomUserCreationForm, GroupForm, ExpenseForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from decimal import Decimal
import json
from .models import Group, GroupMember, Expense, ExpenseShare, Payment, ExpensePayer
from .forms import CustomUserCreationForm, GroupForm, ExpenseForm

def landing_page(request):  
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    user_groups = Group.objects.filter(created_by=request.user)
    return render(request, 'expenses/dashboard.html', {'groups': user_groups})

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            creator_name = f"{request.user.first_name} {request.user.last_name}".strip()
            if not creator_name:  
                creator_name = request.user.username
            
            GroupMember.objects.create(
                group=group,
                name=creator_name,
                email=request.user.email if request.user.email else ''
            )
            
            messages.success(request, f'Group "{group.name}" created successfully! You have been added as a participant.')
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm()
    return render(request, 'expenses/create_group.html', {'form': form})


@login_required
def delete_participant(request, group_id, participant_id):
    group = get_object_or_404(Group, id=group_id)
    participant = get_object_or_404(GroupMember, id=participant_id, group=group)
    
    if group.created_by != request.user:
        messages.error(request, 'You can only delete participants from groups you created.')
        return redirect('dashboard')
    
    creator_name = f"{request.user.first_name} {request.user.last_name}".strip()
    if not creator_name:
        creator_name = request.user.username
    
    if participant.name == creator_name:
        messages.error(request, 'You cannot remove yourself from the group.')
        return redirect('group_detail', group_id=group.id)
    
    participant.delete()
    messages.success(request, f'{participant.name} has been removed from the group.')
    return redirect('group_detail', group_id=group.id)


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.created_by != request.user:
        messages.error(request, 'You can only delete groups you created.')
        return redirect('dashboard')
    
    group_name = group.name
    group.delete()  
    
    messages.success(request, f'Group "{group_name}" has been deleted successfully.')
    return redirect('dashboard')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.created_by != request.user:
        messages.error(request, 'You can only access groups you created.')
        return redirect('dashboard')
    
    participants = GroupMember.objects.filter(group=group).order_by('name')
    expenses = Expense.objects.filter(group=group).order_by('-created_at')
    
    if request.method == 'POST' and 'add_participant' in request.POST:
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        
        if name:
            participant, created = GroupMember.objects.get_or_create(
                group=group, 
                name=name,
                defaults={'email': email, 'phone': phone}
            )
            if created:
                messages.success(request, f'{name} added to group!')
            else:
                messages.warning(request, f'{name} is already in this group!')
        else:
            messages.error(request, 'Name is required!')
        return redirect('group_detail', group_id=group.id)
    
    return render(request, 'expenses/group_detail.html', {
        'group': group,
        'participants': participants,
        'expenses': expenses,
    })


@login_required
def add_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.created_by != request.user:
        messages.error(request, 'You can only add expenses to groups you created.')
        return redirect('dashboard')
    
    participants = GroupMember.objects.filter(group=group).order_by('name')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            
            payer_type = request.POST.get('payer_type', 'single')
            expense.payer_type = payer_type
            
            if payer_type == 'single':
                paid_by_id = request.POST.get('paid_by')
                expense.paid_by = get_object_or_404(GroupMember, id=paid_by_id)
            else:
                expense.paid_by = None
            
            expense.save()
            
            if payer_type == 'multiple':
                payers_data = request.POST.get('payers_data')
                if payers_data:
                    try:
                        payers = json.loads(payers_data)
                        total_paid = Decimal('0')
                        
                        for payer_id, amount_paid in payers.items():
                            total_paid += Decimal(str(amount_paid))
                        
                        if abs(total_paid - expense.amount) > Decimal('0.01'):
                            messages.error(request, f'Total paid ({total_paid}) does not match expense amount ({expense.amount})')
                            expense.delete()
                            return render(request, 'expenses/add_expense.html', {
                                'form': form,
                                'group': group,
                                'participants': participants,
                                'error': 'Payers amounts do not match total amount'
                            })
                        
                        for payer_id, amount_paid in payers.items():
                            if Decimal(str(amount_paid)) > 0:
                                payer = get_object_or_404(GroupMember, id=payer_id)
                                ExpensePayer.objects.create(
                                    expense=expense,
                                    payer=payer,
                                    amount_paid=Decimal(str(amount_paid))
                                )
                    except (json.JSONDecodeError, ValueError) as e:
                        messages.error(request, 'Invalid payer data provided')
                        expense.delete()
                        return render(request, 'expenses/add_expense.html', {
                            'form': form,
                            'group': group,
                            'participants': participants,
                        })
            
            if expense.split_type == 'equal':
                amount_per_person = expense.amount / len(participants)
                for participant in participants:
                    ExpenseShare.objects.create(
                        expense=expense,
                        participant=participant,
                        amount_owed=amount_per_person
                    )
                        
            elif expense.split_type == 'unequal':
                shares_data = request.POST.get('shares_data')
                if shares_data:
                    try:
                        shares = json.loads(shares_data)
                        total_shares = Decimal('0')
                        
                        for participant_id, share_amount in shares.items():
                            total_shares += Decimal(str(share_amount))
                        
                        if abs(total_shares - expense.amount) > Decimal('0.01'):
                            messages.error(request, f'Share amounts ({total_shares}) do not match expense amount ({expense.amount})')
                            expense.delete()
                            return render(request, 'expenses/add_expense.html', {
                                'form': form,
                                'group': group,
                                'participants': participants,
                                'error': 'Shares do not match total amount'
                            })
                        
                        for participant_id, share_amount in shares.items():
                            if Decimal(str(share_amount)) > 0:
                                participant = get_object_or_404(GroupMember, id=participant_id)
                                ExpenseShare.objects.create(
                                    expense=expense,
                                    participant=participant,
                                    amount_owed=Decimal(str(share_amount))
                                )
                    
                    except (json.JSONDecodeError, ValueError) as e:
                        messages.error(request, 'Invalid share data provided')
                        expense.delete()
                        return render(request, 'expenses/add_expense.html', {
                            'form': form,
                            'group': group,
                            'participants': participants,
                        })
            
            messages.success(request, 'Expense added successfully!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'group': group,
        'participants': participants,
    })

@login_required
def settlement(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.created_by != request.user:
        messages.error(request, 'You can only access settlement for groups you created.')
        return redirect('dashboard')
    
    if request.method == 'POST' and 'record_payment' in request.POST:
        paid_by_id = request.POST.get('paid_by_id')
        paid_to_id = request.POST.get('paid_to_id')
        amount = Decimal(request.POST.get('amount'))
        expense_id = request.POST.get('expense_id')
        
        expense = get_object_or_404(Expense, id=expense_id)
        paid_by = get_object_or_404(GroupMember, id=paid_by_id)
        paid_to = get_object_or_404(GroupMember, id=paid_to_id)
        
        Payment.objects.create(
            expense=expense,
            paid_by=paid_by,
            paid_to=paid_to,
            amount=amount
        )
        
        messages.success(request, f'Payment of {amount} {expense.currency} recorded successfully for "{expense.name}"!')
        return redirect('settlement', group_id=group.id)
    
    expenses = Expense.objects.filter(group=group).order_by('-created_at')
    
    expense_debts = []
    
    for expense in expenses:
        expense_shares = ExpenseShare.objects.filter(expense=expense)
        
        expense_payments = Payment.objects.filter(expense=expense)
        
        all_participants = GroupMember.objects.filter(group=group)
        
        balances = {}
        
        if expense.payer_type == 'single':
            for participant in all_participants:
                balances[participant] = Decimal('0')
            
            balances[expense.paid_by] = expense.amount
            
            for share in expense_shares:
                balances[share.participant] -= share.amount_owed
            
        else:
            for participant in all_participants:
                balances[participant] = Decimal('0')
            
            expense_payers = ExpensePayer.objects.filter(expense=expense)
            for expense_payer in expense_payers:
                balances[expense_payer.payer] += expense_payer.amount_paid
            
            for share in expense_shares:
                balances[share.participant] -= share.amount_owed
        
        for payment in expense_payments:
            balances[payment.paid_by] += payment.amount
            balances[payment.paid_to] -= payment.amount
        
        creditors = []
        debtors = []
        
        for participant, balance in balances.items():
            rounded_balance = round(balance, 2)
            if rounded_balance > Decimal('0.01'):
                creditors.append({'participant': participant, 'amount': rounded_balance})
            elif rounded_balance < Decimal('-0.01'):
                debtors.append({'participant': participant, 'amount': -rounded_balance})
        
        debts_list = []
        creditors.sort(key=lambda x: x['amount'], reverse=True)
        debtors.sort(key=lambda x: x['amount'], reverse=True)
        
        i = j = 0
        while i < len(debtors) and j < len(creditors):
            debtor_data = debtors[i]
            creditor_data = creditors[j]
            
            settle_amount = min(debtor_data['amount'], creditor_data['amount'])
            
            if settle_amount > Decimal('0.01'):
                debts_list.append({
                    'debtor': debtor_data['participant'],
                    'creditor': creditor_data['participant'],
                    'amount': round(settle_amount, 2)
                })
            
            debtor_data['amount'] -= settle_amount
            creditor_data['amount'] -= settle_amount
            
            if debtor_data['amount'] <= Decimal('0.01'):
                i += 1
            if creditor_data['amount'] <= Decimal('0.01'):
                j += 1
        
        if debts_list:
            expense_debts.append({
                'expense': expense,
                'debts': debts_list
            })
    
    expense_payments_list = []
    for expense in expenses:
        payments = Payment.objects.filter(expense=expense).order_by('-paid_at')
        if payments.exists():
            expense_payments_list.append({
                'expense': expense,
                'payments': payments
            })
    
    return render(request, 'expenses/settlement.html', {
        'group': group,
        'expense_debts': expense_debts,
        'expense_payments': expense_payments_list,
    })

