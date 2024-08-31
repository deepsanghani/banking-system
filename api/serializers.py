from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Account, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'transaction_type', 'description', 'date']