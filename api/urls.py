from django.urls import path
from . import views

urlpatterns = [
    path('users/create/', views.create_user, name='create_user'),
    path('users/login/', views.login_user, name='login_user'),
    path('account/balance/', views.get_balance, name='get_balance'),
    path('account/deposit/', views.deposit, name='deposit'),
    path('account/withdraw/', views.withdraw, name='withdraw'),
    path('account/transfer/', views.transfer, name='transfer'),
]
