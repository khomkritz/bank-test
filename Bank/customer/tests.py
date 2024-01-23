from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer, Bank, Account, Transfer
from .utils import hash_password
from decimal import Decimal

class BankAPITests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer", email="test@example.com", tel="123456789")
        self.bank = Bank.objects.create(name="Test Bank", code="TST")
        self.account = Account.objects.create(customer=self.customer, balance=1000, bank=self.bank, bank_number="123456789")
        self.transfer_data = {"from_account_id": self.account.id, "to_account_id": self.account.id, "amount": 500}

    def test_create_customer(self):
        client = APIClient()
        url = reverse("customer_create")
        data = {"name": "New Customer", "email": "new@example.com", "tel": "987654321", "password": "test123"}
        
        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Customer.objects.last().name, "New Customer")

    def test_create_account(self):
        client = APIClient()
        url = reverse("account_create")
        data = {"customer_id": self.customer.id, "initial_balance": 1000, "bank_id": self.bank.id, "bank_number": "987654321"}

        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Account.objects.count(), 2)
        self.assertEqual(Account.objects.last().customer.name, "Test Customer")

    def test_transfer_amount(self):
        client = APIClient()
        url = reverse("account_transfer")
        
        response = client.post(url, self.transfer_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertGreaterEqual(Account.objects.get(id=self.account.id).balance, Decimal(self.transfer_data["amount"]))


    def test_account_balance(self):
        client = APIClient()
        url = reverse("account_balance", args=[self.account.id])
        
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["account_id"], self.account.id)
        self.assertEqual(float(response.data["data"]["balance"]), float(self.account.balance))

    def test_transfer_history(self):
        client = APIClient()
        url = reverse("account_transfer_history", args=[self.account.id])
        
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["sent_transfers"]), 0)
        self.assertEqual(len(response.data["data"]["received_transfers"]), 0)