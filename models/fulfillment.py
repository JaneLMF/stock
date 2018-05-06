#!/usr/bin/python
#coding:utf-8

import requests
import datetime, time
import sign
import xml.etree.ElementTree as ET
from urllib import quote, urlencode

import logging

_logger = logging.getLogger(__name__)

ns = {'mws': 'http://mws.amazonaws.com/FulfillmentInboundShipment/2010-10-01/'}
address = {
		'Name': 'cwzy40,LLC',
		'AddressLine1': '2838 Videre Dr',
		'City': 'Wilmington',
		'StateOrProvinceCode': 'DE',
		'PostalCode': '19808',
		'CountryCode': 'US'
		}
class FulfillmentInboundShipment():

	def __init__(self):
		self.AWSAccessKeyId = 'AKIAJFHHTB5XLUZE56AA'
		self.SellerId = 'A3QR4864ATM9Z9'
		self.SecretKey = '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'

	def createInboundShipment(self, shipmentId, destinationFulfillmentCenterId, fromAddress, planItems):
		payload = {
			'Action': 'CreateInboundShipment',
			'AWSAccessKeyId': self.AWSAccessKeyId,
			'SellerId': self.SellerId,
			'SignatureVersion': '2',
			'Timestamp': datetime.datetime.utcnow().isoformat(),
			'Version': '2010-10-01',
			'SignatureMethod': 'HmacSHA256',
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
			

		sorted_payload = sign.sortedAndToStr(payload)
		encryptStr = 'POST' + '\n' + \
			'mws.amazonservices.com' + '\n' + \
			'/FulfillmentInboundShipment/2010-10-01' + '\n' + \
			sorted_payload

		headers = {'Content-Type':'text/xml'}
		url = 'https://mws.amazonservices.com/FulfillmentInboundShipment/2010-10-01?{queryString}&Signature={Signature}'.format(
			queryString=sorted_payload, Signature=quote(sign.getSign(encryptStr, self.SecretKey)))
		_logger.warning(url)
		try:
			r = requests.post(url, headers=headers)
			if r.status_code == 200:
				root = ET.fromstring(r.text)
				shipmentResult = root.find('mws:CreateInboundShipmentResult', ns)
				shipmentId = shipmentResult.find('mws:ShipmentId', ns)
				return {
					"shipmentId": shipmentId.text
				}
			else:
				_logger.warning(r.status_code)
				_logger.warning(r.text)
		except Exception, e:
			_logger.warning(e)
		return None



	def createInboundShipmentPlan(self, planItems, fromAddress):
		payload = {
			'Action': 'CreateInboundShipmentPlan',
			'AWSAccessKeyId': self.AWSAccessKeyId,
			'SellerId': self.SellerId,
			'SignatureVersion': '2',
			'Timestamp': datetime.datetime.utcnow().isoformat(),
			'Version': '2010-10-01',
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

		sorted_payload = sign.sortedAndToStr(payload)
		encryptStr = 'POST' + '\n' + \
			'mws.amazonservices.com' + '\n' + \
			'/FulfillmentInboundShipment/2010-10-01' + '\n' + \
			sorted_payload

		headers = {'Content-Type':'text/xml'}
		url = 'https://mws.amazonservices.com/FulfillmentInboundShipment/2010-10-01?{queryString}&Signature={Signature}'.format(
			queryString=sorted_payload, Signature=quote(sign.getSign(encryptStr, self.SecretKey)))
		
		_logger.warning(url)
		try:
			r = requests.post(url, headers=headers)
			if r.status_code == 200:
				root = ET.fromstring(r.text)
				shipmentPlanResult = root.find('mws:CreateInboundShipmentPlanResult', ns)
				plans = shipmentPlanResult.find('mws:InboundShipmentPlans', ns)
				members = plans.findall('mws:member', ns)
				plans = []
				for member in members:
					plan = {}
					plan['shipmentId'] = member.find('mws:ShipmentId', ns).text
					plan['destinationCenterId'] = member.find('mws:DestinationFulfillmentCenterId', ns).text
					products = []
					items = member.find('mws:Items', ns)
					all_item = items.findall('mws:member', ns)
					for item in all_item:
						product = {}
						product['quantity'] = item.find('mws:Quantity', ns).text
						product['sellerSKU'] = item.find('mws:SellerSKU', ns).text
						product['fulfillmentNetworkSKU'] = item.find('mws:FulfillmentNetworkSKU', ns).text
						products.append(product)
					plan['products'] = products
					plans.append(plan)
				return plans
			else:
				_logger.warning(r.status_code)
				_logger.warning(r.text)
		except Exception, e:
			print e
			_logger.warning(e)
		return None

	def createShipments(self, products):
		plans = self.createInboundShipmentPlan(products, address)
		shipments = []
		for plan in plans:
			shipment = self.createInboundShipment(plan['shipmentId'], plan['destinationCenterId'], address, plan['products'])
			shipments.append(shipment)
		return shipments


	def testPars(self):
		tree = ET.parse('CreateInboundShipmentPlanResponse.xml')
		root = tree.getroot()
		shipmentPlanResult = root.find('mws:CreateInboundShipmentPlanResult', ns)
		plans = shipmentPlanResult.find('mws:InboundShipmentPlans', ns)
		member = plans.find('mws:member', ns)
		fulfillmentCenterId = member.find('mws:DestinationFulfillmentCenterId', ns)
		shipmentId = member.find('mws:ShipmentId', ns)
		items = member.find('mws:Items', ns)
		all_items = items.findall('mws:member', ns)
		plan_product = []
		for item in all_items:
			p = {}
			p['quantity'] = item.find('mws:Quantity', ns).text
			p['sellerSKU'] = item.find('mws:SellerSKU', ns).text
			plan_product.append(p)
		return {
			"shipmentId": shipmentId.text,
			"fulfillmentCenterId": fulfillmentCenterId.text,
			"products": plan_product
		}

	def testParsShipment(self):
		tree = ET.parse('CreateInboundShipmentResponse.xml')
		root = tree.getroot()
		shipmentResult = root.find('mws:CreateInboundShipmentResult', ns)
		shipmentId = shipmentResult.find('mws:ShipmentId', ns)
		return {
			"shipmentId": shipmentId.text
		}

if (__name__ == '__main__'):
	products = [{'sellerSKU': '81A40025US_140', 'quantity': 1, 'asin': 'B077RGJ6S7', 'condition': 'NewItem'},
	{'sellerSKU': 'AN515-51-55WL_612', 'quantity': 1, 'asin': 'B074Q54GSR', 'condition': 'NewItem'}]
	fm = FulfillmentInboundShipment()
	print('result ' + str(fm.createShipments(products)))
	# print fm.testPars()
	# print fm.testParsShipment()
	# plan_result = fm.createInboundShipmentPlan(products, address)
	# if plan_result:
	# 	print fm.createInboundShipment(plan_result['shipmentId'], plan_result['fulfillmentCenterId'], address, plan_result['products'])

	


	

