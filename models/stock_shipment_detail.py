# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from mws_impl import ListInboundShipmentItems
from datetime import datetime

import threading
import random

import logging

_logger = logging.getLogger(__name__)

class ShipmentDetail(models.Model):
	_name = "stock.shipment.detail"

	product_id = fields.Many2one('product.product', 'Product')
	product_tmpl_id = fields.Many2one(
		'product.template', 'Product Template',
		related='product_id.product_tmpl_id',
		help="Technical: used in views")
	move_id = fields.Many2one(
		'stock.move', 'Move')
	create_date = fields.Datetime(string='create time', default=fields.Datetime.now)
	s_create_date = fields.Char(string='create day', compute='_compute_create_date', store=True)
	sku = fields.Char(string="sku")
	asin = fields.Char(string="asin")
	asin_url = fields.Char(string="asin_url", compute='_compute_asin_url', store=True)
	condition = fields.Char(string="condition")
	quantity = fields.Float(string='shipment quantity')
	aws_received = fields.Float(string='shipment reveived quantity')
	shipment_id = fields.Char(string="shipment id")
	state = fields.Char(string="shipment state")
	matched_received = fields.Boolean(string="aws received have bee matched quantity", default=False)

	@api.one
	def action_fetch_fba_quantity(self):
		_logger.info("action_fetch_fba_quantity shipment_id '%s'" % str(self.shipment_id))
		download_thread = threading.Thread(target=self._full_aws_received)
		download_thread.start()
		return True		

	def _full_aws_received(self):
		with api.Environment.manage():
			# As this function is in a new thread, I need to open a new cursor, because the old one may be closed
			new_cr = self.pool.cursor()
			self = self.with_env(self.env(cr=new_cr))
			try:
				changed = False
				listShipment = ListInboundShipmentItems()
				for r in self:
					_logger.info("sku '%s' shipment_id '%s' matched_received %s" % (str(r.sku), str(r.shipment_id), str(r.matched_received)))
					if not r.matched_received:
						products = listShipment.getShipmentsByShipmentId(r.shipment_id)
						sku_products = [x for x in products if x['SellerSKU'] == r.sku]
						quantity_received = float(sku_products[0].get('QuantityReceived'))
						if quantity_received == r.quantity:
							r.matched_received = True
						_logger.info("sku '%s' shipment_id '%s'  quantity %s quantity_received %s matched_received %s" % (str(r.sku), str(r.shipment_id), str(r.quantity), str(quantity_received), str(r.matched_received)))
						r.aws_received = quantity_received
						changed = True
				if changed:
					new_cr.commit()
			except Exception, e:
				_logger.error('getShipmentsByShipmentId catch exception:' + e.message)
			finally:
				new_cr.close()
			return {}

	def _compute_create_date(self):
		for record in self:
			try:
				t = datetime.strptime(record.create_date, '%d-%m-%Y %H:%M:%S').strftime('%m-%d-%Y')
			except Exception as e:
				t = datetime.strptime(record.create_date, '%Y-%m-%d %H:%M:%S').strftime('%m-%d-%Y')
			record.s_create_date = t

	@api.depends('asin')
	def _compute_asin_url(self):
		for record in self:
			_logger.info(record.asin);
			# record.asin_url = '<a href="%s%s">%s</a>' % ('https://www.amazon.com/dp/', record.asin, record.asin)
			record.asin_url = 'https://www.amazon.com/dp/%s' % record.asin
