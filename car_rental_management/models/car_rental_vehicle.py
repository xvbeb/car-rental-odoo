from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalVehicle(models.Model):
    """Store vehicles available in the car rental fleet."""

    _name = "car.rental.vehicle"
    _description = "Rental Vehicle"
    _order = "name, id"

    name = fields.Char(required=True)
    license_plate = fields.Char(required=True, index=True)
    vin = fields.Char(string="VIN", copy=False)
    category_id = fields.Many2one(
        "car.rental.vehicle.category",
        required=True,
        ondelete="restrict",
    )
    location_id = fields.Many2one(
        "car.rental.location",
        required=True,
        ondelete="restrict",
    )
    daily_rate = fields.Monetary(required=True, default=0.0)
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    odometer = fields.Integer(default=0)
    state = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("rented", "Rented"),
            ("maintenance", "Maintenance"),
        ],
        required=True,
        default="available",
    )
    image_1920 = fields.Image()
    booking_ids = fields.One2many(
        "car.rental.booking",
        "vehicle_id",
        string="Bookings",
    )
    inspection_ids = fields.One2many(
        "car.rental.inspection",
        "vehicle_id",
        string="Inspections",
    )
    damage_ids = fields.One2many(
        "car.rental.damage",
        "vehicle_id",
        string="Damages",
    )
    active = fields.Boolean(default=True)

    _license_plate_unique = models.Constraint(
        "UNIQUE(license_plate)",
        "A vehicle with this license plate already exists.",
    )
    _vin_unique = models.Constraint(
        "UNIQUE(vin)",
        "A vehicle with this VIN already exists.",
    )

    @api.constrains("daily_rate", "odometer")
    def _check_nonnegative_values(self):
        """Prevent negative rental rates and odometer values."""
        for vehicle in self:
            if vehicle.daily_rate < 0 or vehicle.odometer < 0:
                raise ValidationError(
                    "Daily rate and odometer values cannot be negative."
                )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        """Use the category rate when a vehicle category is selected."""
        if self.category_id:
            self.daily_rate = self.category_id.default_daily_rate
