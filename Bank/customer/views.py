from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Account, Transfer, Bank, Token
from .utils import hash_password, check_password, generate_jwt_tokens, refresh_jwt_token, verify_jwt_token

class login(APIView):
    def post(self, request):
        data = request.data
        if "email" not in data or data["email"] == None:
            return Response({"status" : False,"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        customer = Customer.objects.get(email=data["email"])
        check = check_password(data["password"], customer.password)
        if check == True:
            token = generate_jwt_tokens(customer.id)
            Token.objects.create(customer_id=customer.id, access_token=token["access_token"], refresh_token=token["refresh_token"])
        else:
            return Response({"status" : False,"message": "Password is not true"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status" : True, "message" : "login success", "data" : token}, status=status.HTTP_200_OK)

class Refresh(APIView):
    def post(self, request):
        data = request.data
        refresh = refresh_jwt_token(data["refresh_token"])
        Token.objects.create(customer_id=refresh["customer_id"], access_token=refresh["access_token"], refresh_token=refresh["refresh_token"])
        return Response({"status" : True, "message" : "refresh success", "data" : refresh}, status=status.HTTP_200_OK)
    
class logout(APIView):
    def post(self, request):
        payload = verify_jwt_token(request)
        if payload["status"] == False:
            return Response({"status" : False,"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        Token.objects.filter(customer_id=payload["customer_id"]).delete()
        return Response({"status" : True, "message" : "logout success"}, status=status.HTTP_200_OK)

class CustomerList(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        customer_list = []
        for customer in customers:
            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'email' : customer.email,
                'tel' : customer.tel,
                'update_at' : customer.update_at,
                'create_at' : customer.create_at
            }
            customer_list.append(customer_data)
        return Response({"status" : True, "message" : "get success","data" : customer_list}, status=status.HTTP_200_OK)

class CustomerCreate(APIView):
    def post(self, request):
        data = request.data
        if "name" not in data or data["name"] == None:
            return Response({"status" : False,"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)
        password = hash_password(data["password"])
        data["password"] = password
        customer = Customer.objects.create(**data)
        return Response({"status" : True, "message" : "create success","data" : {"id" : customer.id, "name" : customer.name}}, status=status.HTTP_200_OK)
    
class BankList(APIView):
    def get(self, request):
        banks = Bank.objects.all()
        banks_list = []
        for bank in banks:
            customer_data = {
                'id': bank.id,
                'name': bank.name,
                'code' : bank.code,
            }
            banks_list.append(customer_data)
        return Response({"status" : True, "message" : "get success","data" : banks_list}, status=status.HTTP_200_OK)
    
class AccountList(APIView):
    def get(self, request, customer_id):
        # payload = verify_jwt_token(request)
        # if payload["status"] == False:
        #     return Response({"status" : False,"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        # customer_id = payload["customer_id"]
        account_list = []
        accounts = Account.objects.filter(customer=customer_id)
        for account in accounts:
            data_account = {
                "id" : account.id,
                "customer" : {
                    "name" : account.customer.name,
                    "email" : account.customer.email,
                    "tel" : account.customer.tel
                },
                "bank" : {
                    "name" : account.bank.name,
                    "code" : account.bank.code,
                },
                "bank_number" : account.bank_number,
                "balance" : account.balance,
                "update_at" : account.update_at,
                "create_at" : account.create_at
            }
            account_list.append(data_account)
        return Response({"status" : True, "message" : "get success","data" : account_list}, status=status.HTTP_200_OK)

class AccountCreate(APIView):
    def post(self, request):
        data = request.data
        # payload = verify_jwt_token(request)
        # if payload["status"] == False:
        #     return Response({"status" : False,"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        # customer_id = payload["customer_id"]
        if "customer_id" not in data:
            return Response({"status" : False, "message": 'Customer ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if "initial_balance" not in data:
            return Response({"status" : False, "message": 'Initial Balance is required'}, status=status.HTTP_400_BAD_REQUEST)
        if "bank_number" not in data:
            return Response({"status" : False, "message": 'Bank Number is required'}, status=status.HTTP_400_BAD_REQUEST)
        customer = Customer.objects.get(id=data["customer_id"])
        bank = Bank.objects.get(id=data["bank_id"])
        account = Account.objects.create(customer=customer, balance=data["initial_balance"], bank=bank, bank_number=data["bank_number"])
        return Response({"status" : True, "message" : "create success", "data" : {'account_id': account.id, 'customer_id': customer.id, 'initial_balance': data["initial_balance"]}}, status=status.HTTP_200_OK)

class AccountBalance(APIView):
    def get(self, request, account_id):
        # payload = verify_jwt_token(request)
        # if payload["status"] == False:
        #     return Response({"status" : False,"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        # customer_id = payload["customer_id"]
        account = Account.objects.get(id=account_id)
        return Response({"status" : True, "message" : "get success","data" : {'account_id': account.id, 'balance': str(account.balance), 'bank' : { 'name' : account.bank.name, 'code' : account.bank.code }, 'bank_number' : account.bank_number}}, status=status.HTTP_200_OK)

class AccountTransferHistory(APIView):
    def get(self, request, account_id):
        # payload = verify_jwt_token(request)
        # if payload["status"] == False:
        #     return Response({"status" : False,"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        # customer_id = payload["customer_id"]
        account = Account.objects.get(id=account_id)
        transfers_sent = Transfer.objects.filter(from_account=account)
        transfers_received = Transfer.objects.filter(to_account=account)
        
        sent_data = [{'to_account': transfer.to_account.id, 'amount': str(transfer.amount), 'name' : transfer.to_account.customer.name, 'bank_name' : transfer.to_account.bank_number, 'create_at' : transfer.create_at} for transfer in transfers_sent]
        received_data = [{'from_account': transfer.from_account.id, 'amount': str(transfer.amount),  'name' : transfer.from_account.customer.name, 'bank_name' : transfer.from_account.bank_number, 'create_at' : transfer.create_at} for transfer in transfers_received]

        return Response({"status" : True, "message" : "get success", "data" : {'sent_transfers': sent_data, 'received_transfers': received_data}}, status=status.HTTP_200_OK)

class AccountTransfer(APIView):
    def post(self, request):
        data = request.data
        # payload = verify_jwt_token(request)
        # if payload["status"] == False:
        #     return Response({"status" : False,"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        # customer_id = payload["customer_id"]
        from_account_id = request.data.get('from_account_id')
        to_account_id = request.data.get('to_account_id')
        amount = request.data.get('amount')
        if "from_account_id" not in data:
            return Response({"status" : False, "message" : "From Account ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if "to_account_id" not in data:
            return Response({"status" : False, "message" : "To Account ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if "amount" not in data:
            return Response({"status" : False, "message" : "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        from_account = Account.objects.get(id=from_account_id)
        to_account = Account.objects.get(id=to_account_id)

        if from_account.balance < amount:
            return Response({"status" : False, "message" : "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        Transfer.objects.create(from_account=from_account, to_account=to_account, amount=amount)
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()
        return Response({"status" : True, "message": "Transfer successful"}, status=status.HTTP_200_OK)