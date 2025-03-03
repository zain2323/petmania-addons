# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ShowWizardMessage(models.TransientModel):
	_name = "show.wizard.message"
	_description = "Show Wizard Message"

	text = fields.Text()
	
	def show_wizard_message(self,message,name='Message/Summary'):
		partial_id = self.create({'text':message}).id
		return {
			'name':name,
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'show.wizard.message',
			'res_id': partial_id.id,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'domain': '[]',
		}
