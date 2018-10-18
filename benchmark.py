#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy
from datetime import datetime
import random
import erppeek


_QTY_FOR_AVERAGE = 3
_SALE_ORDER_LINE_QTY = [1, 2, 5, 10, 20, 50, 100, 200]


VERSIONS = {
    10: {"url": "http://instance_mag_10.dy", "database": "benchmark"},
    12: {"url": "http://instance_grap_12.dy/", "database": "benchmark"},
}


###############################################################################
# Connection Odoo
def init_odoo(configuration):
    odoo = erppeek.Client(configuration.get('url'))
    odoo.login(
        configuration.get('login', 'admin'),
        password=configuration.get('password', 'admin'),
        database=configuration.get('database'))
    return odoo


###############################################################################
# Create Sale Order
def _create_sale_order(partner, products_data, line_qty, version=False):
    line_vals = []
    for i in range(line_qty):
        product_data = products_data[
            random.randint(0, len(products_data) - 1)]

        line_vals.append((0, 0, {
            'product_id': product_data['id'],
            'name': product_data['name'],
            'product_uom_qty': random.randint(1, 1000),
            'price_unit': random.randint(10, 100),
        }))
    order_vals = {
        'partner_id': partner.id,
        'order_line': line_vals,

    }
    order = odoo.SaleOrder.create(order_vals)
    return order


###############################################################################
# Create Picking from sale Order
def _confirm_order(order, version=False):
    order.action_confirm()


###############################################################################
# Create Invoice from sale Order
def _invoice_order(order, version=False):
    wizard = odoo.SaleAdvancePaymentInv.create({})
    wizard.create_invoices(context={'active_ids': [order.id]})


###############################################################################
# Logging function
def _log_result(durations, line_qty):
    print (
        "- {} lines. Duration (global): {:6.2f}"
        ". Duration (Per Line): {:6.3f}").format(
            str(line_qty).zfill(5),
            numpy.mean(durations), numpy.mean(durations) / line_qty)

###############################################################################
# Main Script
###############################################################################
for version in VERSIONS.keys():
    odoo = init_odoo(VERSIONS[version])
    orders_dict = {}

    # Load Data
    partner = odoo.ResPartner.browse([('customer', '=', True)])[0]
    products_data = odoo.ProductProduct.read([
        ('sale_ok', '=', True),
        ('type', '=', 'product'),
        ('invoice_policy', '=', 'order'),
    ], ['id', 'name'])

    # Sale Order Creation
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print "CREATE SALE ORDER (Version %s)" % (version)
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    for line_qty in _SALE_ORDER_LINE_QTY:
        orders_dict[line_qty] = []
        durations = []
        for i in range(_QTY_FOR_AVERAGE):
            begin_date = datetime.now()
            order = _create_sale_order(
                partner, products_data, line_qty, version)
            orders_dict[line_qty].append(order)
            end_date = datetime.now()
            delta = end_date - begin_date
            durations.append((delta).total_seconds())
        _log_result(durations, line_qty)

    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print "CREATE STOCK PICKING (Version %s)" % (version)
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    # Create Picking from Sale Order
    for line_qty in _SALE_ORDER_LINE_QTY:
        durations = []
        for i in range(_QTY_FOR_AVERAGE):
            begin_date = datetime.now()
            order = orders_dict[line_qty][i]
            _confirm_order(order)
            end_date = datetime.now()
            delta = end_date - begin_date
            durations.append((delta).total_seconds())
        _log_result(durations, line_qty)

    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print "CREATE INVOICE (Version %s)" % (version)
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    # Create Invoices from Sale Order
    for line_qty in _SALE_ORDER_LINE_QTY:
        durations = []
        for i in range(_QTY_FOR_AVERAGE):
            begin_date = datetime.now()
            order = orders_dict[line_qty][i]
            _invoice_order(order)
            end_date = datetime.now()
            delta = end_date - begin_date
            durations.append((delta).total_seconds())
        _log_result(durations, line_qty)
