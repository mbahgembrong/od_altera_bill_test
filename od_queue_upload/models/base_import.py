from odoo import api, fields, models


class Import(models.TransientModel):
    _inherit = 'base_import.import'


    def do(self, fields, columns, options, dryrun=False):
        self.ensure_one()
        if dryrun:
            result = super(Import, self).do(fields, columns, options, dryrun=dryrun)
            return result
        else:
            self.with_delay().do_delayed(fields, columns, options)
        return {
            'ids': [],
            'messages': [{}],
            'nextrow': 0,
        }

    def _do(self, fields, columns, options, dryrun=False, messages=[]):
        result = super(Import, self).do(fields, columns, options, dryrun=dryrun)
        next_row = result.get('nextrow', 0)
        messages += result.get('messages')
        if next_row != 0:
            options['skip'] += next_row
            return self._do(fields, columns, options, dryrun, messages)
        return {
            'nextrow': 0,
            'messages': messages,
        }

    def do_delayed(self, fields, columns, options, messages=[]):
        self.ensure_one()
        result = self._do(fields, columns, options, dryrun=False, messages=messages)
        model = self.env['ir.model'].search([('model', '=', self.res_model)], limit=1)
        model_name = False
        if model:
            model_name = model.name
        if result.get('messages'):
            message = 'File uploaded with errors %s :' % model_name
            for res in result.get('messages'):
                message += res.get('message') + '\n'
        else:
            message = 'File uploaded successfully %s' % model_name
        user = self.env.user
        partner = user.partner_id
        if partner.email:
            self._send_mail(partner.email, 'File Upload', message)
        return True

    def _send_mail(self, mail_to, subject, body):
        mail = self.env['mail.mail']
        mail_from = self.env['ir.mail_server'].search([], limit=1).smtp_user or 'service@odoo.com'
        mail.create({
            'email_from': mail_from,
            'email_to': mail_to,
            'subject': subject,
            'body_html': body,
        }).send()
