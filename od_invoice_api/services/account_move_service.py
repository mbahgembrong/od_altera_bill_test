from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

class AccountMoveService(Component):
    _name = "account.move.service"
    _inherit = "base.rest.service"
    _usage = "account_move"
    _collection = "v1.private"
    _description = """Account Move Service"""

    def _res_validator(self):
        return {
            'code': {'type': 'integer'},
            'status': {'type': 'string'},
            'message': {'type': 'string'},
            'data': {'type': 'list'}
        }

    @restapi.method(
        [(['/'], 'GET')],
        input_param=Datamodel("search.input"),
        output_param=restapi.CerberusValidator('_res_validator'),
        auth='api_key',
    )
    def search(self, params):
        search = params.search
        move_type = params.move_type
        order = params.order or "ASC"
        limit = params.limit or 10
        offset = params.offset or 0
        domain = []
        if search:
            domain.append(('name', 'ilike', search))
        if move_type:
            domain.append(('move_type', '=', move_type.value))
        result = self.env['account.move'].search(domain, limit=limit, offset=offset, order="id %s"% order)
        res = {
            'code': 200,
            'status': 'success',
            'data': self._get_account_move_output(result)
        }
        return res

    @restapi.method(
        [(['/<int:id>/show/'], 'GET')],
        output_param=restapi.CerberusValidator('_res_validator'),
        auth='api_key',
    )
    def show(self, id):
        result = self.env['account.move'].browse(id)
        if result:
            res = {
                'code': 200,
                'status': 'success',
                'data': self._get_account_move_output([result])
            }
        else:
            res = {
                'code': 404,
                'status': 'Failed',
                'message': 'Account Move not found'
            }
        return res

    @restapi.method(
    [(['/create'], 'POST')],
    input_param=Datamodel("account.move.input.list"),
    output_param=restapi.CerberusValidator('_res_validator'),
    auth='api_key',
    )
    def create(self, body):
        try:
            result = self._create(body)
            res = {
                'code': 200,
                'status': 'success',
            }
        except Exception as e:
            res = {
                'code': 404,
                'status': 'Failed',
                'message': str(e)
            }
        return res

    @restapi.method(
        [(['/<int:id>/update'], 'PUT')],
        input_param=Datamodel("account.move.input"),
        output_param=restapi.CerberusValidator('_res_validator'),
        auth='api_key',
    )
    def update(self, id, body):
        result = self.env['account.move'].browse(id)
        if result:
            try:
                if body.partner:
                    partner = self._get_or_fail_partner(body.partner)
                else:
                    partner = self.env['res.partner'].browse(result.partner_id.id)
                if body.move_type:
                    move_type = self._get_move_type(body.move_type.value)
                if body.top:
                    top_id = self._get_or_fail_top(body.top).id
                    date_due = False
                else:
                    top_id = False
                    date_due = body.due_date
                account_lines = []
                for line in (body.lines or []):
                    account_lines.append((0, 0, {
                        'product_id': line.product_id,
                        'quantity': line.quantity,
                        'price_unit': line.unit_price,
                        'discount': line.discount,
                        'account_id': line.account_id,
                        'tax_ids': line.tax_ids
                    }))
                result.write({
                    'partner_id': partner.id or result.partner_id.id,
                    'payment_reference': body.payment_reference,
                    'invoice_date': body.invoice_date or result.invoice_date,
                    'invoice_date_due': date_due or result.invoice_date_due,
                    'invoice_payment_term_id': top_id or result.invoice_payment_term_id.id,
                    'move_type': move_type or result.move_type,
                    'invoice_line_ids': account_lines or result.invoice_line_ids
                })
                res = {
                    'code': 200,
                    'status': 'success',
                }
            except Exception as e:
                res = {
                    'code': 404,
                    'status': 'Failed',
                    'message': str(e)
                }
        else:
            res = {
                'code': 404,
                'status': 'Failed',
                'message': 'Account Move not found'
            }
        return res


    @restapi.method(
        [(['/<int:id>/delete'], 'DELETE')],
        output_param=restapi.CerberusValidator('_res_validator'),
        auth='api_key',
    )
    def destroy(self, id):
        result = self.env['account.move'].browse(id)
        if result:
            result.unlink()
            res = {
                'code': 200,
                'status': 'success',
            }
        else:
            res = {
                'code': 404,
                'status': 'Failed',
                'message': 'Account Move not found'
            }
        return res


    @restapi.method(
        [(['/<int:id>/register_payment'], 'POST')],
        input_param=Datamodel("register.payment.input"),
        output_param=restapi.CerberusValidator('_res_validator'),
        auth='api_key',
    )
    def register_payment(self, id, body):
        result = self.env['account.move'].browse(id)
        if result:
            try:
                payment_method_id = body.payment_method_id
                partner_bank_id = body.partner_bank_id
                amount = body.amount
                payment_date = body.payment_date
                memo = body.memo
                account_move = self.env['account.move'].browse(id)
                if not account_move:
                    raise Exception('Account Move not found')
                if account_move.state != 'posted':
                    raise Exception('Account Move not posted')
                line_ids = account_move.line_ids.filtered(lambda x: x.account_id.user_type_id.type in ['receivable', 'payable'])
                if not line_ids:
                    raise Exception('No receivable/payable account found in this invoice')

                payment = self.env['account.payment.register'].create({
                    'payment_date':payment_date,
                    'journal_id': payment_method_id,
                    'partner_bank_id': partner_bank_id,
                    'amount': amount,
                    'communication': memo or account_move.payment_reference or account_move.name,
                    'partner_id': account_move.partner_id.id,
                    'line_ids': [(6, 0, line_ids.ids)]
                })
                payment.sudo().action_create_payments()
                res = {
                    'code': 200,
                    'status': 'success',
                }
            except Exception as e:
                res = {
                    'code': 404,
                    'status': 'Failed',
                    'message': str(e)
                }
        else:
            res = {
                'code': 404,
                'status': 'Failed',
                'message': 'Account Move not found'
            }
        return res

    def _create(self, body):
        result = self.env['account.move']
        for account_move in body.account_move_inputs:
            account_lines = []
            partner = self._get_or_fail_partner(account_move.partner)
            move_type = self._get_move_type(account_move.move_type.value)
            if account_move.top:
                top_id = self._get_or_fail_top(account_move.top).id
                date_due = False
            else:
                top_id = False
                date_due = account_move.due_date

            for line in account_move.lines:
                account_lines.append((0, 0, {
                    'product_id': line.product_id,
                    'quantity': line.quantity,
                    'price_unit': line.unit_price,
                    'discount': line.discount,
                    'account_id': line.account_id,
                    'tax_ids': line.tax_ids
                }))
            result += self.env['account.move'].create({
                'partner_id': partner.id,
                'payment_reference': account_move.payment_reference,
                'invoice_date': account_move.invoice_date,
                'invoice_date_due': date_due,
                'invoice_payment_term_id': top_id,
                'journal_id': account_move.journal_id,
                'move_type': move_type,
                'invoice_line_ids': account_lines
            })
        return result

    def _get_account_move_output(self, account_moves):
        result = []
        for account_move in account_moves:
            lines = []
            for line in account_move.invoice_line_ids:
                lines.append({
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'unit_price': line.price_unit,
                    'discount': line.discount,
                    'account_id': line.account_id.id,
                    'tax_ids': line.tax_ids.ids
                })
            result.append({
                'id': account_move.id,
                'partner': account_move.partner_id.name,
                'payment_reference': account_move.payment_reference,
                'replace_invoice': account_move.payment_reference,
                'invoice_date': account_move.invoice_date,
                'due_date': account_move.invoice_date_due,
                'top': account_move.invoice_payment_term_id.name,
                'move_type': account_move.move_type,
                'journal_id': account_move.journal_id.id,
                'lines': lines
            })
        return result
    def _get_or_fail_partner(self, partner):
        result = self.env['res.partner'].search([('name', '=', partner)], limit=1)
        if not result:
            result = self.env['res.partner'].create({
                'name': partner,
                'is_company': True
            })
        return result

    def _get_move_type(self, move_type):
        if move_type == 'Customer Invoice':
            return 'out_invoice'
        elif move_type == 'Credit Note':
            return 'out_refund'
        elif move_type == 'Vendor Bill':
            return 'in_invoice'
        elif move_type == 'Vendor Credit Note':
            return 'in_refund'
        else:
            return 'entry'


    def _get_or_fail_top(self, top):
        top = self.env['account.payment.term'].search([('name', '=', top)], limit=1)
        if not top:
            top = self.env['account.payment.term'].create({
                'name': top
            })
        return top

    
