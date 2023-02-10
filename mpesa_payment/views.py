import requests
import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient
from .utils import MpesaGateWay
from .validators import *


from .models import *

cl = MpesaGateWay()

def mpesa_payment(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = int(request.POST['amount'])
        business_short_code = 174379
        account_reference = 'Reference'
        transaction_desc = 'Description'
        callback_url = 'https://9ffd-41-90-68-152.in.ngrok.io/mpesa-payment/response'

        if phone_number[0] == "+":
            phone_number = phone_number[1:]
        if phone_number[0] == "0":
            phone_number = "254" + phone_number[1:]
        try:
            validate_possible_number(phone_number, "KE")
        except:
            messages.info(request, 'Phone number is invalid')
            return redirect('mpesa')
        
        if not amount or amount <= 0:
            messages.info(request, 'Amount should be greater that 0')
            return redirect('mpesa')

        response = cl.stk_push_request(business_short_code=business_short_code, phone_number=int(phone_number), amount=amount, account_reference=account_reference, transaction_desc=transaction_desc, callback_url=callback_url)

        
        #transactions = Transactions.objects.create(checkout_request_id=checkout_request_id)
        
        return redirect('response_data')

    else:
        return render(request, 'mpesa.html')


def response_view(request):
    data = json.loads(request.body.decode('utf-8'))

    return HttpResponse(data)

def response_data(request):
    payload = requests.get('https://9ffd-41-90-68-152.in.ngrok.io/mpesa-payment/response')
    print(payload)

    return HttpResponse('PAYLOAD')

