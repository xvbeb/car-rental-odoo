from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalDamage(models.Model):
    """Track damage detected on rental vehicles."""

    _name = "car.rental.damage"
    _description = "Vehicle Damage"
    _order = "detected_date desc, id desc"

    name = fields.Char(required=True)
    vehicle_id = fields.Many2one(
        "car.rental.vehicle",
        required=True,
        ondelete="cascade",
    )
    inspection_id = fields.Many2one(
        "car.rental.inspection",
        ondelete="set null",
    )
    detected_date = fields.Date(required=True, default=fields.Date.context_today)
    severity = fields.Selection(
        [("minor", "Minor"), ("medium", "Medium"), ("major", "Major")],
        required=True,
        default="minor",
    )
    state = fields.Selection(
        [("reported", "Reported"), ("repairing", "Repairing"), ("fixed", "Fixed")],
        required=True,
        default="reported",
    )
    repair_cost = fields.Monetary(default=0.0)
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Text()
    image = fields.Image()

    @api.constrains("repair_cost")
    def _check_repair_cost(self):
        """Prevent negative estimated or actual repair costs."""
        for damage in self:
            if damage.repair_cost < 0:
                raise ValidationError("Repair cost cannot be negative.")
