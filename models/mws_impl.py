#!/usr/bin/python
#coding:utf-8

import abc
import requests
import datetime, time
import sign
import xml.etree.ElementTree as ET
from urllib import quote, urlencode

import hmac
import hashlib
import base64

import logging

_logger = logging.getLogger(__name__)

address = {
		'Name': 'cwzy40,LLC',
		'AddressLine1': '2838 Videre Dr',
		'City': 'Wilmington',
		'StateOrProvinceCode': 'DE',
		'PostalCode': '19808',
		'CountryCode': 'US'
		}

NS_HOST = 'mws.amazonaws.com'
HOST = 'mws.amazonservices.com'
URL = 'https://%s/' % HOST
AWSAccessKeyId = 'AKIAJFHHTB5XLUZE56AA'
SellerId = 'A3QR4864ATM9Z9'
SecretKey = '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'

class MwsRequest(object):
	__metaclass__= abc.ABCMeta

	def __init__(self, section, operation):
		self.query = {
			'Action': operation,
			'AWSAccessKeyId': AWSAccessKeyId,
			'SellerId': SellerId,
			'SignatureVersion': '2',
			'Version': '2010-10-01',
			'SignatureMethod': 'HmacSHA256',
			'Timestamp': None
		}
		self.section = section
		self.operation = operation
		self.params = None
		self.ns = None

	def version(self, y, m, d):
		self.query['Version'] = "%4d-%02d-%02d" % (y, m, d)
	
	def setDeadline(self, p):
		self.query['Timestamp'] = p.isoformat()

	def set_param(self, p):
		self.params = p

	def get_signature(self, content):
		signature = hmac.new(
				bytearray(SecretKey),
				msg=content,
				digestmod=hashlib.sha256
				)
		return base64.b64encode(signature.digest()).decode()

	def sortedAndToStr(self, data):
		sorted_data = sorted(data.iteritems())
		return urlencode(sorted_data).replace('+', '%20')

	def get_headers(self):
		return {'Content-Type':'text/xml'}

	def get_url(self):
		if not self.query['Timestamp']:
			self.setDeadline(datetime.datetime.utcnow())
		sorted_payload = self.sortedAndToStr(dict(self.query.items() + self.params.items()) if self.params else self.query)
		encryptStr = 'POST' + '\n' + \
			HOST + '\n' + \
			'/' + self.section + '/' + self.query['Version'] + '\n' + \
			sorted_payload
		self.ns = {'mws': 'http://%s/%s/%s/' % (NS_HOST, self.section, self.query['Version'])}
		return URL + self.section + '/' + self.query['Version'] + '?' + sorted_payload + '&Signature=' + quote(self.get_signature(encryptStr))

	@abc.abstractmethod
	def parse_body(self, body):
		pass

	def get_text(self, p_obj, c_tag):
		if p_obj is not None:
			c_obj = p_obj.find('mws:' + c_tag, self.ns)
			if c_obj is not None:
				return c_obj.text
		return None
				

	def submit(self):
		url = self.get_url()
		try:
			r = requests.post(url, headers=self.get_headers())
			if r.status_code == 200:
				return self.parse_body(r.text)
			else:
				if __name__ == '__main__':
					print(r.status_code)
					print(r.text)
				else:
					_logger.warning(r.status_code)
					_logger.warning(r.text)

		except Exception, e:
			if __name__ == '__main__':
				print(e)
			else:
				_logger.warning(e)
		return None
		
class CreateInboundShipmentPlan(MwsRequest):
	def __init__(self):
		super(CreateInboundShipmentPlan, self).__init__('FulfillmentInboundShipment', 'CreateInboundShipmentPlan')

	def createInboundShipmentPlan(self, planItems, fromAddress):
		payload = {
			'SignatureMethod': 'HmacSHA256',
			'ShipFromAddress.Name': fromAddress['Name'],
			'ShipFromAddress.AddressLine1': fromAddress['AddressLine1'],
			'ShipFromAddress.City': fromAddress['City'],
			'ShipFromAddress.StateOrProvinceCode': fromAddress['StateOrProvinceCode'],
			'ShipFromAddress.PostalCode': fromAddress['PostalCode'],
			'ShipFromAddress.CountryCode': fromAddress['CountryCode']
		}

		for index in range(len(planItems)):
			number = str(index + 1)
			payload['InboundShipmentPlanRequestItems.member.'+ number + '.SellerSKU'] = planItems[index]['sellerSKU']
			payload['InboundShipmentPlanRequestItems.member.'+ number + '.Quantity'] = planItems[index]['quantity']
			payload['InboundShipmentPlanRequestItems.member.'+ number + '.ASIN'] = planItems[index]['asin']
			payload['InboundShipmentPlanRequestItems.member.'+ number + '.Condition'] = planItems[index]['condition']

		self.set_param(payload)
		return self.submit()

	def parse_body(self, body):
		root = ET.fromstring(body)
		shipmentPlanResult = root.find('mws:CreateInboundShipmentPlanResult', self.ns)
		plans = shipmentPlanResult.find('mws:InboundShipmentPlans', self.ns)
		members = plans.findall('mws:member', self.ns)
		plans = []
		for member in members:
			plan = {}
			plan['shipmentId'] = member.find('mws:ShipmentId', self.ns).text
			plan['destinationCenterId'] = member.find('mws:DestinationFulfillmentCenterId', self.ns).text
			products = []
			items = member.find('mws:Items', self.ns)
			all_item = items.findall('mws:member', self.ns)
			for item in all_item:
				product = {}
				product['quantity'] = item.find('mws:Quantity', self.ns).text
				product['sellerSKU'] = item.find('mws:SellerSKU', self.ns).text
				product['fulfillmentNetworkSKU'] = item.find('mws:FulfillmentNetworkSKU', self.ns).text
				products.append(product)
			plan['products'] = products
			plans.append(plan)
		return plans

class CreateInboundShipment(MwsRequest):
	def __init__(self):
		super(CreateInboundShipment, self).__init__('FulfillmentInboundShipment', 'CreateInboundShipment')

	def createInboundShipment(self, shipmentId, destinationFulfillmentCenterId, fromAddress, planItems):
		payload = {
			'ShipmentId': shipmentId,
			'InboundShipmentHeader.ShipmentName': datetime.datetime.utcnow().isoformat(),
			'InboundShipmentHeader.ShipFromAddress.Name': fromAddress['Name'],
			'InboundShipmentHeader.ShipFromAddress.AddressLine1': fromAddress['AddressLine1'],
			'InboundShipmentHeader.ShipFromAddress.City': fromAddress['City'],
			'InboundShipmentHeader.ShipFromAddress.StateOrProvinceCode': fromAddress['StateOrProvinceCode'],
			'InboundShipmentHeader.ShipFromAddress.PostalCode': fromAddress['PostalCode'],
			'InboundShipmentHeader.ShipFromAddress.CountryCode': fromAddress['CountryCode'],
			'InboundShipmentHeader.DestinationFulfillmentCenterId': destinationFulfillmentCenterId,
			'InboundShipmentHeader.ShipmentStatus': 'WORKING',
			'InboundShipmentHeader.LabelPrepPreference': 'SELLER_LABEL'
		}
		for index in range(len(planItems)):
			number = str(index + 1)
			payload['InboundShipmentItems.member.'+ number + '.SellerSKU'] = planItems[index]['sellerSKU']
			payload['InboundShipmentItems.member.'+ number + '.QuantityShipped'] = planItems[index]['quantity']
			payload['InboundShipmentItems.member.'+ number + '.FulfillmentNetworkSKU'] = planItems[index]['fulfillmentNetworkSKU']
		self.set_param(payload)
		return self.submit()

	def parse_body(self, body):
		print(body)
		root = ET.fromstring(body)
		shipmentResult = root.find('mws:CreateInboundShipmentResult', self.ns)
		shipmentId = shipmentResult.find('mws:ShipmentId', self.ns)
		return {
			"shipmentId": shipmentId.text
		}

	def createShipments(self, products):
		c_plans = CreateInboundShipmentPlan()
		plans = c_plans.createInboundShipmentPlan(products, address)
		shipments = []
		for plan in plans:
			shipment = self.createInboundShipment(plan['shipmentId'], plan['destinationCenterId'], address, plan['products'])
			shipment['products'] = plan['products']
			shipments.append(shipment)
		return shipments

class ListInboundShipmentItemsByNextToken(MwsRequest):
	def __init__(self):
		section = 'FulfillmentInboundShipment'
		operation = 'ListInboundShipmentItemsByNextToken'
		super(ListInboundShipmentItemsByNextToken, self).__init__(section, operation)

	def parse_body(self, body):
		root = ET.fromstring(body)
		itemsResult = root.find('mws:ListInboundShipmentItemsByNextTokenResult', self.ns)
		item = itemsResult.find('mws:ItemData', self.ns)

		next_token = self.get_text(itemsResult, 'NextToken')
		members = item.findall('mws:member', self.ns)
		received_products = []
		for member in members:
			p = {}
			p['ShipmentId'] = member.find('mws:ShipmentId', self.ns).text
			p['SellerSKU'] = member.find('mws:SellerSKU', self.ns).text
			p['QuantityReceived'] = member.find('mws:QuantityReceived', self.ns).text
			p['QuantityShipped'] = member.find('mws:QuantityShipped', self.ns).text
			received_products.append(p)
		return {"nextToken": next_token, "data": received_products}

class ListInboundShipmentItems(MwsRequest):
	def __init__(self):
		super(ListInboundShipmentItems, self).__init__('FulfillmentInboundShipment', 'ListInboundShipmentItems')

	def parse_body(self, body):
		root = ET.fromstring(body)
		itemsResult = root.find('mws:ListInboundShipmentItemsResult', self.ns)
		item = itemsResult.find('mws:ItemData', self.ns)
		next_token = itemsResult.find('mws:NextToken', self.ns).text
		members = item.findall('mws:member', self.ns)
		received_products = []
		for member in members:
			p = {}
			p['ShipmentId'] = member.find('mws:ShipmentId', self.ns).text
			p['SellerSKU'] = member.find('mws:SellerSKU', self.ns).text
			p['QuantityReceived'] = member.find('mws:QuantityReceived', self.ns).text
			p['QuantityShipped'] = member.find('mws:QuantityShipped', self.ns).text
			received_products.append(p)
		return {"nextToken": next_token, "data": received_products}

	def getShipmentsByShipmentId(self, shipmentId):
		self.set_param({'ShipmentId': shipmentId})
		shipments = []
		next_token = None
		f_shipments = self.submit()
		next_token = f_shipments['nextToken']
		shipments = f_shipments['data'] + shipments
		while next_token:
			list_next = ListInboundShipmentItemsByNextToken()
			list_next.set_param({'NextToken': next_token})
			n_shipments = list_next.submit()
			if n_shipments:
				next_token = n_shipments['nextToken']
				shipments = n_shipments['data'] + shipments
			else:
				next_token = None
		return shipments

if (__name__ == '__main__'):

	# products = [{'sellerSKU': '81A40025US_140', 'quantity': 500, 'asin': 'B077RGJ6S7', 'condition': 'NewItem'},
	# {'sellerSKU': 'AN515-51-55WL_612', 'quantity': 500, 'asin': 'B074Q54GSR', 'condition': 'NewItem'}]

	# fm = CreateInboundShipment()
	# print('result ' + str(fm.createShipments(products)))

	# print fm.testPars()
	# print fm.testParsShipment()
	# plan_result = fm.createInboundShipmentPlan(products, address)
	# if plan_result:
	# 	print fm.createInboundShipment(plan_result['shipmentId'], plan_result['fulfillmentCenterId'], address, plan_result['products'])

	r = ListInboundShipmentItems()
	shipments = r.getShipmentsByShipmentId('FBA15CRBSQ41')
	print(len(shipments))
	print(shipments)

	# s = 'AAAAAAAAAAC+tgW17QOkHUViBOrM1C8MXAEAAAAAAAA4ewW4An/axPBSJsp9BHdqALm/oZSIJFmMoQuHptFIRZO09ZgOp+tyJdhIBPanPc7HDVHUPI8o9MKe2jpqh7ak/TQkWA7qbJYYcU4GAfy4HPM/PsZRnFlZf3ZdqeCkVDO9Uvg0Bd2eF/0up5xj0/C19zkErpWW2WDRTyK0nE+I480x29BGr7AfljrDCMSirupaGLGAUpZi0aBYkgWT5PFdEADDMYiKUFsTiugkq8K9jPeqxhGAr6nd/t9+pIlvrcuq38SLCa0/8ew945uub6HrNOgz3hcN2D8YPKcT3x/9VX5QLJgQ6oRUJjAyw8TCkKLyvGT4sAB98jmKVB76ro9wrnmoBrjKzuBp37kVYfz4U4NQOg9dr+NafqHBqy6YY91Fr7bSb46VOZ5VVRp0UNcDoFPdiYUe8UEjwIVfb+lqC6d8eOVUGQKjw5GT1Fkx4smFJTIJTxuKRAFI62s=';
	# print(quote(s))
	# params=[('name1','2838 Videre Dr /'), ('name1','abc/def'), ('name2','value21')]
	# print(urlencode(params))
	# print(quote('2838 Videre Dr /'))
	# print(quote('2838+Videre+Dr /'))





