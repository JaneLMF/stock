# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from mws_impl import ListInboundShipmentItems

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
	create_date = fields.Datetime(string='create time', default=fields.Datetime.now)
	sku = fields.Char(string="sku")
	asin = fields.Char(string="asin")
	condition = fields.Char(string="condition")
	quantity = fields.Float(string='shipment quantity')
	aws_received = fields.Float(string='shipment reveived quantity', compute='_compute_aws_reeived')
	shipment_id = fields.Char(string="shipment id")
	state = fields.Char(string="shipment state")

	def _full_aws_received(self):
		with api.Environment.manage():
			# As this function is in a new thread, I need to open a new cursor, because the old one may be closed
			new_cr = self.pool.cursor()
			self = self.with_env(self.env(cr=new_cr))
			try:
				changed = False
				listShipment = ListInboundShipmentItems()
				for r in self:
					products = listShipment.getShipmentsByShipmentId(r.shipment_id)
					sku_products = [x for x in products if x['SellerSKU'] == r.sku]
					r.aws_received = sku_products[0].get('QuantityReceived')
					changed = True
				if changed:
					new_cr.commit()
			except Exception, e:
				_logger.error('getShipmentsByShipmentId catch exception:' + e.message)
			finally:
				new_cr.close()
			return {}

	@api.depends('sku', 'shipment_id', 'product_id')	
	def _compute_aws_reeived(self):
		_logger.info('enter the _compute_aws_reeived')
		# _logger.warning("_compute_aws_reeived find_product product_id " + str(self.product_id))
		download_thread = threading.Thread(target=self._full_aws_received)
		download_thread.start()
		return True
