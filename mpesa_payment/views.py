from django.shortcuts import render, redirect
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient

def mpesa_payment(request):
    cl = MpesaClient()
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = int(request.POST['amount'])
        account_reference = 'reference'
        transaction_desc = 'Description'
        callback_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        
        

        return HttpResponse(response)
        
    else:
        return render(request, 'mpesa.html')

def stk_push_callback(request):
    data = request.body
    
    return HttpResponse("STK Push in Django👋")
