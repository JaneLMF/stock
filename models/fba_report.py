# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
class ReportInfo(models.Model):
	_name = "fba.report.info"
	_description = "Record report update info"

	name = fields.Char('Report Name', required=True)
	update_date = fields.Datetime(string='Recently Update Date')
	from_date = fields.Datetime(string='Update From Date')
	end_date = fields.Datetime(string='Update End Date')
	next_update_date = fields.Datetime(string='Next Update Date')

class SettlementReport(models.Model):
    _name = "fba.report.settlement"
    _description = "Settlement Report For FBA"

    settlement_id = fields.Char('Settlement Id', required=True)
    deposit_date = fields.Char('Deposit Date')
    transaction_type = fields.Char('Transaction Type')
    order_id = fields.Char('Order Id')
    merchant_order_id = fields.Char('Merchant Order Id')
    adjustment_id = fields.Char('Adjustment Id')
    shipment_id = fields.Char('Shipment Id')
    marketplace_name = fields.Char('Marketplace Name')
    shipment_fee_type = fields.Char('Shipment Fee Type')
    shipment_fee_amount = fields.Float('Shipment Fee Amount')
    order_fee_type = fields.Char('Order Fee Type')
    order_fee_amount = fields.Char('Order Fee Amount')
    fulfillment_id = fields.Char('Fulfillment Id')
    posted_date = fields.Char('Posted Date')
    order_item_code = fields.Char('Order Item Code')
    merchant_order_item_id = fields.Char('Merchant Order Item Id')
    merchant_adjustment_item_id = fields.Char('Merchant Adjustment Item Id')
    sku = fields.Char('SKU')
    quantity_purchased = fields.Integer('Quantity Purchased')
    price_type = fields.Char('Price Type')
    price_amount = fields.Float('Price Amount')
    item_related_fee_type = fields.Char('Item Related Fee Type')
    item_related_fee_amount = fields.Float('Item Related Fee Amount')
    misc_fee_amount = fields.Float('Misc Fee Amount')
    other_fee_amount = fields.Float('Other Fee Amount')
    other_fee_reason_description = fields.Char('Other Fee Reason Description')
    direct_payment_amount = fields.Float('Direct Payment Amount')
    other_amount = fields.Float('other Amount')
    order_date = fields.Char('Order Date')

class RemovalReport(models.Model):
	_name = "fba.report.removal"
	_description = "Removal Report For FBA"

	request_date = fields.Char('Request Date')
	order_id = fields.Char('Order Id')
	order_type = fields.Char('Order Type')
	order_status = fields.Char('Order Status')
	last_updated_date = fields.Char('Last Updated Date')
	sku = fields.Char('SKU')
	fnsku = fields.Char('Fnsku')
	disposition = fields.Char('Disposition')
	requested_quantity = fields.Integer('Requested Quantity')
	cancelled_quantity = fields.Integer('Cancelled Quantity')
	disposed_quantity = fields.Integer('Disposed Quantity')
	shipped_quantity = fields.Integer('Shipped Quantity')
	in_process_quantity = fields.Integer('In Process Quantity')
	removal_fee = fields.Float('Removal Fee')
	currency = fields.Char('Currency')

class ReturnsReport(models.Model):
	_name = "fba.report.returns"
	_description = "Returns Report For FBA"

	return_date = fields.Char('Return Date')
	order_id = fields.Char('Order Id')
	sku = fields.Char('SKU')
	asin = fields.Char('Asin')
	fnsku = fields.Char('Fnsku')
	product_name = fields.Char('Product Name')
	quantity = fields.Integer('Quantity')
	fulfillment_center_id = fields.Char('Fulfillment Center Id')
	detailed_disposition = fields.Char('Detailed Disposition')
	reason = fields.Char('Reason')
	status = fields.Char('Status')
	license_plate_number = fields.Char('License Plate Number')
	customer_comments = fields.Char('Customer Comments')
