from marshmallow import fields,Schema
from odoo.addons.datamodel.core import Datamodel

class AccountMoveLineInput(Datamodel):
    _name = "account.move.line.input"
    _description = 'Account Move Line Input'

    product_id = fields.Integer(required=True)
    quantity = fields.Float(required=True)
    unit_price = fields.Float(required=True)
    discount = fields.Float()
    account_id = fields.Integer()
    tax_ids = fields.List(fields.Integer())