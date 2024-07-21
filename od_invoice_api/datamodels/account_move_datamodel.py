import enum

from marshmallow import fields,Schema
from odoo.addons.datamodel.core import Datamodel
from odoo.addons.od_invoice_api.datamodels.account_move_line_datamodel import AccountMoveLineInput


class JournalEnum(enum.Enum):
    invoice = "Customer Invoice"
    credit_note = "Credit Note"
    vendor_bill = "Vendor Bill"
    vendor_credit_note = "Vendor Credit Note"
    misc = "Miscellaneous"

class SearchInput(Datamodel):
    _name = "search.input"
    _description = 'Search Input'

    search = fields.String()
    move_type = fields.Enum(JournalEnum)
    order = fields.String()
    limit = fields.Integer()
    offset = fields.Integer()


class AccountMoveInput(Datamodel):
    _name = "account.move.input"
    _description = 'Account Move Input'

    partner = fields.String(required=True)
    payment_reference = fields.String()
    invoice_date = fields.Date(required=True)
    due_date = fields.Date()
    top = fields.String()
    move_type = fields.Enum(JournalEnum, required=True)
    journal_id = fields.Integer()
    lines = fields.List(fields.Nested(AccountMoveLineInput.get_schema()))

class AccountMoveInputList(Datamodel):
    _name = "account.move.input.list"
    _description = 'Account Move Input List'
    _is_list = True

    account_move_inputs = fields.List(fields.Nested(AccountMoveInput.get_schema()))

class AccountMoveOutput(Datamodel):
    _name = "account.move.output"
    _inherit = "account.move.input"
    _description = 'Account Move Output'

    id = fields.Integer()

class AccountMoveOutputList(Datamodel):
    _name = "account.move.output.list"
    _description = 'Account Move Output List'

    account_move_outputs = fields.List(fields.Nested(AccountMoveOutput.get_schema()))


class RegisterPaymentInput(Datamodel):
    _name = "register.payment.input"
    _description = 'Register Payment Input'

    payment_method_id = fields.Integer(required=True)
    partner_bank_id = fields.Integer()
    amount = fields.Float(required=True)
    payment_date = fields.Date(required=True)
    memo = fields.String()

