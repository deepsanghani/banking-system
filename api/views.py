from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from .models import Account, Transaction
from .serializers import UserSerializer, AccountSerializer, TransactionSerializer
from bankingsystem.tasks import generate_monthly_statements

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        Account.objects.create(user=user)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    account = request.user.account
    serializer = AccountSerializer(account)
    generate_monthly_statements.delay()
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    amount = request.data.get('amount')
    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    if amount <= 0:
        return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    account = request.user.account
    account.balance += amount
    account.save()
    Transaction.objects.create(
        user=request.user,
        amount=amount,
        transaction_type='credit',
        description='Deposit'
    )
    return Response({'balance': account.balance}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    amount = request.data.get('amount')
    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    account = request.user.account
    if account.balance >= amount:
        account.balance -= amount
        account.save()
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            transaction_type='debit',
            description='Withdrawal'
        )
        return Response({'balance': account.balance}, status=status.HTTP_200_OK)

    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    target_user_id = request.data.get('target_user_id')
    amount = request.data.get('amount')
    if not target_user_id or not amount:
        return Response({'error': 'Target user ID and amount are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    if request.user.id == int(target_user_id):
        return Response({'error': 'Cannot transfer to yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        target_account = Account.objects.get(user_id=target_user_id)
    except Account.DoesNotExist:
        return Response({'error': 'Target user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    account = request.user.account
    if account.balance >= amount:
        account.balance -= amount
        target_account.balance += amount
        account.save()
        target_account.save()
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            transaction_type='debit',
            description=f'Transfer to user {target_user_id}'
        )
        Transaction.objects.create(
            user=target_account.user,
            amount=amount,
            transaction_type='credit',
            description=f'Transfer from user {request.user.id}'
        )
        return Response({'balance': account.balance}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
