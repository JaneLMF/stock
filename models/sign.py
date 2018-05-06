#!/usr/bin/python
#coding:utf-8
import hmac
import hashlib
import base64
import binascii
from urllib import quote


# &Signature=i58bMEyQfI7%2Bk8Zagzjcd8GF3x2%2BjTXSPLjFxiCKtXw%3D
# HmacSHA256
def getSign(content, secret):
	signature = hmac.new(
	    bytearray(secret),
	    msg=content,
	    digestmod=hashlib.sha256
	    )
	return base64.b64encode(signature.digest()).decode()

def getSha1(content, secret):
	my_sign = hmac.new(secret, content, hashlib.sha1).digest()
	my_signbase = base64.b64encode(my_sign)
	return my_signbase

def sortedAndToStr(data):
	sorted_str = ''
	sorted_data = sorted(data.keys())
	sorted_data_len = len(sorted_data)
	for i in range(len(sorted_data)):
		key = str(sorted_data[i])
		value = quote(str(data[key]))
		sorted_str = (sorted_str + key + '=' + value)
		if i < sorted_data_len - 1:
			sorted_str = sorted_str + '&'
	return sorted_str

if (__name__ == '__main__'):
	API_SECRET = 'q7T2oaGjxnjpCYjF7qAHMh3aiJnxP2tDzZpYeZqs'
	message = 'POST' + '\n' + \
			'mws.amazonservices.com.cn' + '\n' + \
			'/' + '\n' + \
			'AWSAccessKeyId=AKIAJFHHTB5XLUZE56AA&Action=GetReportList&Merchant=A3QR4864ATM9Z9&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp=2018-04-25T02%3A10%3A13Z&Version=2009-01-01'
# Action=CreateInboundShipmentPlan&AWSAccessKeyId=AKIAJFHHTB5XLUZE56AA&SellerId=A3QR4864ATM9Z9&SignatureVersion=2&Timestamp=2018-04-24T17%3A08%3A50.495115&Version=2010-10-01&SignatureMethod=HmacSHA1&ShipFromAddress.Name=cwzy40,LLC&ShipFromAddress.AddressLine1=2838 Videre Dr&ShipFromAddress.City=Wilmington&ShipFromAddress.StateOrProvinceCode=DE&ShipFromAddress.PostalCode=19808&ShipFromAddress.CountryCode=01&InboundShipmentPlanRequestItems.member.1.SellerSKU=81A40025US_140&InboundShipmentPlanRequestItems.member.1.Quantity=30
	# message = 'POST' + '\n' + \
	# 		'mws.amazonservices.com' + '\n' + \
	# 		'/' + '\n' + \
	# 		'SignatureVersion=2&AWSAccessKeyId=AKIAJFHHTB5XLUZE56AA&Timestamp=2018-04-24T17%3A25%3A19.992021&SignatureMethod=HmacSHA1&Version=2010-10-01&Action=CreateInboundShipmentPlan&SellerId=A3QR4864ATM9Z9'
	print getSign(message, API_SECRET)
	# print base64.b64encode(bytearray('209cdeb8618d476b8dd3967da1cdab349c1180cc5281d15628b39977371d0492'))