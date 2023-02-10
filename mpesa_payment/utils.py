import logging
import time
import math
import base64
import requests

from datetime import datetime
from requests.auth import HTTPBasicAuth
from requests import Response
from phonenumber_field.phonenumber import PhoneNumber

from notification_django.settings import env
from .models import Transactions
from .exceptions import *
from .validators import *
#from .serializers import TransactionSerializer

logging = logging.getLogger("default")

now = datetime.now()

class MpesaResponse(Response):
	response_description = ""
	error_code = None
	error_message = ''


def mpesa_response(r):
	"""
	Create MpesaResponse object from requests.Response object
	
	Arguments:
		r (requests.Response) -- The response to convert
	"""

	r.__class__ = MpesaResponse
	json_response = r.json()
	r.response_description = json_response.get('ResponseDescription', '')
	r.error_code = json_response.get('errorCode')
	r.error_message = json_response.get('errorMessage', '')
	return r



class MpesaGateWay:
    business_short_code = None
    consumer_key = None
    consumer_secret = None
    access_token_url = None
    access_token = None
    access_token_expiration = None
    checkout_url = None
    timestamp = None


    def __init__(self):
        now = datetime.now()
        self.business_short_code = env("business_short_code")
        self.consumer_key = env("consumer_key")
        self.consumer_secret = env("consumer_secret")
        self.access_token_url = env("access_token_url")

        self.password = self.generate_password()
        self.callback_url = env("callback_url")
        self.checkout_url = env("checkout_url")

        try:
            self.access_token = self.getAccessToken()
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            logging.error("Error {}".format(e))
        else:
            self.access_token_expiration = time.time() + 34000000000545667856343556667

    def getAccessToken(self):
        try:
            res = requests.get(self.access_token_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
            print(res)
        except Exception as err:
            logging.error("Error {}".format(err))
            raise err
        else:
            token = res.json()["access_token"]
            self.headers = {"Authorization": "Bearer %s" % token, "Content-type":"application/json"}
            return token

    class Decorators:
        @staticmethod
        def refreshToken(decorated):
            def wrapper(gateway, *args, **kwargs):
                if (gateway.access_token_expiration and time.time() > gateway.access_token_expiration):
                    token = gateway.getAccessToken()
                    gateway.access_token = token
                return decorated(gateway, *args, **kwargs)

            return wrapper


    def generate_password(self):
        """Generates mpesa api password using the provided shortcode and passkey"""
        self.timestamp = now.strftime("%Y%m%d%H%M%S")
        password_str = "174379" + env("pass_key") + self.timestamp
        password_bytes = password_str.encode("ascii")
        return base64.b64encode(password_bytes).decode("utf-8")

    @Decorators.refreshToken
    def stk_push_request(self, business_short_code, phone_number, amount, account_reference, transaction_desc, callback_url):

        if str(account_reference).strip() == '':
            raise MpesaInvalidParameterException('Account reference cannot be blank')
        
        if str(transaction_desc).strip() == '':
            raise MpesaInvalidParameterException('Transaction description cannot be blank')

        if not isinstance(amount, int):
            raise MpesaInvalidParameterException('Amount must be an integer')

        mpesa_environment = env('mpesa_environment')

        

        req_data = {
            "BusinessShortCode": business_short_code,
            "Password": base64.b64encode((str(business_short_code) + env('pass_key') + self.timestamp).encode('ascii')).decode('utf-8'),
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }
        
        try:
            res_data = requests.post(self.checkout_url, json=req_data, headers=self.headers)
            #response = mpesa_response(res_data)
            response = res_data.json()
            print(self.headers)
            return response
        except requests.exceptions.ConnectionError:
            raise MpesaConnectionError('Connection failed')
        except Exception as ex:
            raise MpesaConnectionError(str(ex))
        
        
        """
        if res.ok:
            data["checkout_request_id"] = res_data["CheckoutRequestID"]

            Transaction.objects.create(**data)
        
        
        
    
    def check_status(self, data):
        try:
            status = data["Body"]["stkCallback"]["ResultCode"]
        except Exception as e:
            logging.error(f"Error: {e}")
            status = 1
        return status

    
    def get_transaction_object(data):
        checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        transaction, _ = Transaction.objects.get_or_create(
            checkout_request_id=checkout_request_id
        )

        return transaction

    def handle_successful_pay(self, data, transaction):
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        for item in items:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                receipt_no = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]

        transaction.amount = amount
        transaction.phone_number = PhoneNumber(raw_input=phone_number)
        transaction.receipt_no = receipt_no
        transaction.confirmed = True

        return transaction

    def callback_handler(self, data):
        status = self.check_status(data)
        transaction = self.get_transaction_object(data)
        if status==0:
            self.handle_successful_pay(data, transaction)
        else:
            transaction.status = 1

        transaction.status = status
        transaction.save()

        transaction_data = TransactionSerializer(transaction).data

        logging.info("Transaction completed info {}".format(transaction_data))

        return Response({"status": "ok", "code": 0}, status=200)

    """