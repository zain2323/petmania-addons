from odoo import models, fields, api
from datetime import datetime


class Pet(models.Model):
    _name = 'vet.pet'
    _description = 'Pet Information'

    name = fields.Char('Pet Name', required=True)
    owner_id = fields.Many2one('res.partner', string='Owner', required=True, ondelete='cascade')
    species = fields.Selection([
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('bird', 'Bird'),
        ('reptile', 'Reptile'),
        ('other', 'Other')
    ], string='Species', required=True)
    breed = fields.Char('Breed')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknown', 'Unknown')
    ], string='Gender', default='unknown')
    date_of_birth = fields.Date('Date of Birth')
    age = fields.Char(compute='_compute_age', string='Age', store=False)
    medical_condition = fields.Text('Medical Condition')
    image = fields.Binary('Image', attachment=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for pet in self:
            if pet.date_of_birth:
                today = fields.Date.today()
                delta = today - pet.date_of_birth
                years = delta.days // 365
                months = (delta.days % 365) // 30
                if years > 0:
                    pet.age = f"{years} year(s) {months} month(s)"
                else:
                    pet.age = f"{months} month(s)"
            else:
                pet.age = "Unknown"