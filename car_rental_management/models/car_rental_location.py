from odoo import fields, models


class CarRentalLocation(models.Model):
    """Represent a vehicle pickup and return location."""

    _name = "car.rental.location"
    _description = "Car Rental Location"
    _order = "name, id"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Contact Address",
        ondelete="restrict",
    )
    phone = fields.Char()
    email = fields.Char()
    vehicle_ids = fields.One2many(
        "car.rental.vehicle",
        "location_id",
        string="Vehicles",
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "A rental location with this code already exists.",
    )
