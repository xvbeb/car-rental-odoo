from odoo import fields, models


class CarRentalVehicleCategory(models.Model):
    """Classify rental vehicles and define default rental conditions."""

    _name = "car.rental.vehicle.category"
    _description = "Rental Vehicle Category"
    _order = "sequence, name, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    default_daily_rate = fields.Monetary(required=True, default=0.0)
    deposit_amount = fields.Monetary(default=0.0)
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    vehicle_ids = fields.One2many(
        "car.rental.vehicle",
        "category_id",
        string="Vehicles",
    )
    active = fields.Boolean(default=True)

    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "A vehicle category with this name already exists.",
    )
