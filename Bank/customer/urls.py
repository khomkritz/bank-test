from django.urls import path, include
from customer import views

urlpatterns = [
    path('customer_list', views.CustomerList.as_view()),
    path('customer_create', views.CustomerCreate.as_view(), name='customer_create'),
    path('account_create', views.AccountCreate.as_view(), name='account_create'),
    path('bank_list', views.BankList.as_view()),
    path('account_list/<int:customer_id>', views.AccountList.as_view()),
    path('account_create', views.AccountCreate.as_view()),
    path('account_balance/<int:account_id>', views.AccountBalance.as_view(), name='account_balance'),
    path('account_transfer', views.AccountTransfer.as_view(), name='account_transfer'),
    path('account_transfer_history/<int:account_id>', views.AccountTransferHistory.as_view(), name='account_transfer_history'),
]