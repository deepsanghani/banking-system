from celery import shared_task
from decimal import Decimal
from datetime import datetime
from api.models import User, MonthlyStatement, Transaction

def get_user_transactions(user):
    transactions = Transaction.objects.filter(user=user).values('amount', 'transaction_type', 'date')
    return list(transactions)

def calculate_mab(transactions):
    if not transactions:
        return Decimal('0.00')
    daily_balances = {}
    for t in transactions:
        transaction_date = datetime.fromisoformat(t['date']).date()
        amount = Decimal(t['amount']) if t['transaction_type'] == 'credit' else -Decimal(t['amount'])
        if transaction_date not in daily_balances:
            daily_balances[transaction_date] = Decimal('0.00')
        daily_balances[transaction_date] += amount
    total_days = len(daily_balances)
    if total_days == 0:
        return Decimal('0.00')
    total_balance = sum(daily_balances.values())
    mab = total_balance / Decimal(total_days)
    return mab

@shared_task
def generate_monthly_statements():
    print("Task started")
    users = User.objects.all()
    for user in users:
        transactions = get_user_transactions(user)
        for t in transactions:
            t['amount'] = float(Decimal(t['amount']))
            t['date'] = t['date'].isoformat()
        
        debit = sum(Decimal(t['amount']) for t in transactions if t['transaction_type'] == 'debit')
        credit = sum(Decimal(t['amount']) for t in transactions if t['transaction_type'] == 'credit')
        mab = calculate_mab(transactions)
        num_transactions = len(transactions)
        MonthlyStatement.objects.update_or_create(
            user=user,
            month=datetime.now().strftime('%Y-%m'),
            defaults={
                'transactions': [
                    {**t, 'amount': float(Decimal(t['amount'])), 'date': t['date']} for t in transactions
                ],
                'debit': float(debit),
                'credit': float(credit),
                'mab': float(mab),
                'num_transactions': num_transactions
            }
        )
