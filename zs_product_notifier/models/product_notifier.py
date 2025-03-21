# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductNotifierConfig(models.Model):
    _name = 'product.notifier.config'
    _description = 'Product Change Notification Configuration'

    name = fields.Char(string='Name', required=True)
    notification_email = fields.Char(string='Notification Email', required=True)
    active = fields.Boolean(default=True)

    notify_on_archive = fields.Boolean(string='Notify when Product Archived/Unarchived', default=True)
    notify_on_create = fields.Boolean(string='Notify when Product Created', default=True)
    notify_on_unlink = fields.Boolean(string='Notify when Product Deleted', default=True)
    notify_on_price_change = fields.Boolean(string='Notify when Price Changed', default=True)

    @api.constrains('notification_email')
    def _check_email_validity(self):
        for record in self:
            if record.notification_email and not '@' in record.notification_email:
                raise ValidationError("Please enter a valid email address")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Override create method to send notification
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        self._send_product_notification('create', res)
        return res

    # Override write method to detect changes
    def write(self, vals):
        # Check if active status is changing
        archive_change = 'active' in vals

        # Check if prices are changing
        price_change = 'list_price' in vals or 'standard_price' in vals

        res = super(ProductTemplate, self).write(vals)

        # Send notifications based on change type
        if archive_change:
            self._send_product_notification('archive', self)

        if price_change:
            self._send_product_notification('price_change', self)

        return res

    # Override unlink method
    def unlink(self):
        # Store product names before deletion
        product_names = self.mapped('name')

        # Send notification before actual deletion
        self._send_product_notification('unlink', self)

        return super(ProductTemplate, self).unlink()

    def _send_product_notification(self, change_type, products):
        """Send email notification for product changes"""
        configs = self.env['product.notifier.config'].sudo().search([('active', '=', True)])
        if not configs:
            return

        for config in configs:
            # Skip if the notification for this change type is disabled
            if (change_type == 'archive' and not config.notify_on_archive) or \
                    (change_type == 'create' and not config.notify_on_create) or \
                    (change_type == 'unlink' and not config.notify_on_unlink) or \
                    (change_type == 'price_change' and not config.notify_on_price_change):
                continue

            email_to = config.notification_email

            # Prepare email content based on change type
            if change_type == 'create':
                subject = f"New Product Created: {products.name}"
                body = f"""
                <h3 style="color:#1a73e8;">New Product Created</h3>
                <div style="margin-left:10px;">
                    <p><strong>Name:</strong> {products.name}</p>
                    <p><strong>Internal Reference:</strong> {products.default_code or 'N/A'}</p>
                    <p><strong>Sales Price:</strong> {products.list_price}</p>
                    <p><strong>Cost Price:</strong> {products.standard_price}</p>
                </div>
                """

            elif change_type == 'archive':
                for product in products:
                    subject = f"Product {'Archived' if not product.active else 'Unarchived'}: {product.name}"
                    body = f"""
                    <h3 style="color:#1a73e8;">Product {'Archived' if not product.active else 'Unarchived'}</h3>
                    <div style="margin-left:10px;">
                        <p><strong>Name:</strong> {product.name}</p>
                        <p><strong>Internal Reference:</strong> {product.default_code or 'N/A'}</p>
                    </div>
                    """

                    # Send email for each product
                    self._send_email(email_to, subject, body)

                # Return here as we've already sent emails for each product
                return

            elif change_type == 'unlink':
                if isinstance(products, models.Model):
                    product_names = products.mapped('name')
                else:
                    product_names = products

                subject = f"Product(s) Deleted"
                body = f"""
                <h3 style="color:#1a73e8;">Products Deleted</h3>
                <div style="margin-left:10px;">
                """
                for name in product_names:
                    body += f"<p>- {name}</p>"
                body += "</div>"

            elif change_type == 'price_change':
                for product in products:
                    subject = f"Price Changed for Product: {product.name}"
                    body = f"""
                    <h3 style="color:#1a73e8;">Product Price Updated</h3>
                    <div style="margin-left:10px;">
                        <p><strong>Name:</strong> {product.name}</p>
                        <p><strong>Internal Reference:</strong> {product.default_code or 'N/A'}</p>
                        <p><strong>Sales Price:</strong> {product.list_price}</p>
                        <p><strong>Cost Price:</strong> {product.standard_price}</p>
                    </div>
                    """

                    # Send email for each product
                    self._send_email(email_to, subject, body)

                # Return here as we've already sent emails for each product
                return

            # Send the email (for cases other than archive and price_change)
            self._send_email(email_to, subject, body)

    def _send_email(self, email_to, subject, body):
        """Helper method to send email"""
        _logger.critical("sending email")
        try:
            mail_template = self.env.ref('zs_product_notifier.email_template_product_change_notification')
            ctx = {
                'email_to': email_to,
                'subject': subject,
                'body_html': body,
            }
            mail_template.with_context(ctx).send_mail(self.env.user.id, force_send=True)
            _logger.info(f"Product notification email sent to {email_to}")
        except Exception as e:
            _logger.error(f"Failed to send product notification email: {str(e)}")
