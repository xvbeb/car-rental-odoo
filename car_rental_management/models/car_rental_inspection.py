from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalInspection(models.Model):
    """Record vehicle condition at pickup, return, or maintenance."""

    _name = "car.rental.inspection"
    _description = "Vehicle Inspection"
    _order = "inspection_datetime desc, id desc"

    name = fields.Char(required=True)
    vehicle_id = fields.Many2one(
        "car.rental.vehicle",
        required=True,
        ondelete="cascade",
    )
    booking_id = fields.Many2one(
        "car.rental.booking",
        ondelete="set null",
    )
    inspection_type = fields.Selection(
        [
            ("pickup", "Pickup"),
            ("return", "Return"),
            ("maintenance", "Maintenance"),
        ],
        required=True,
        default="pickup",
    )
    inspection_datetime = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
    )
    inspector_id = fields.Many2one(
        "res.users",
        required=True,
        default=lambda self: self.env.user,
        ondelete="restrict",
    )
    odometer = fields.Integer()
    fuel_level = fields.Float(string="Fuel Level, %", default=100.0)
    damage_ids = fields.One2many(
        "car.rental.damage",
        "inspection_id",
        string="Damages",
    )
    notes = fields.Text()

    @api.constrains("odometer", "fuel_level")
    def _check_measurements(self):
        """Validate odometer and fuel level measurements."""
        for inspection in self:
            if inspection.odometer < 0:
                raise ValidationError("Odometer value cannot be negative.")
            if not 0 <= inspection.fuel_level <= 100:
                raise ValidationError("Fuel level must be between 0 and 100 percent.")
