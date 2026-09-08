from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalBooking(models.Model):
    """Manage customer reservations and active vehicle rentals."""

    _name = "car.rental.booking"
    _description = "Car Rental Booking"
    _order = "date_from desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    customer_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="restrict",
    )
    vehicle_id = fields.Many2one(
        "car.rental.vehicle",
        required=True,
        ondelete="restrict",
    )
    pickup_location_id = fields.Many2one(
        "car.rental.location",
        required=True,
        ondelete="restrict",
    )
    return_location_id = fields.Many2one(
        "car.rental.location",
        required=True,
        ondelete="restrict",
    )
    date_from = fields.Datetime(required=True, default=fields.Datetime.now)
    date_to = fields.Datetime(required=True)
    day_count = fields.Integer(compute="_compute_amounts", store=True)
    daily_rate = fields.Monetary(required=True)
    total_amount = fields.Monetary(compute="_compute_amounts", store=True)
    currency_id = fields.Many2one(
        "res.currency",
        related="vehicle_id.currency_id",
        store=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("active", "Active"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    inspection_ids = fields.One2many(
        "car.rental.inspection",
        "booking_id",
        string="Inspections",
    )
    notes = fields.Text()

    @api.depends("date_from", "date_to", "daily_rate")
    def _compute_amounts(self):
        """Compute billable days and the total booking amount."""
        for booking in self:
            if booking.date_from and booking.date_to:
                seconds = (booking.date_to - booking.date_from).total_seconds()
                booking.day_count = max(1, int((seconds + 86399) // 86400))
            else:
                booking.day_count = 0
            booking.total_amount = booking.day_count * booking.daily_rate

    @api.constrains("date_from", "date_to")
    def _check_rental_period(self):
        """Require the return date to be later than the pickup date."""
        for booking in self:
            if booking.date_from and booking.date_to <= booking.date_from:
                raise ValidationError(
                    "The return date must be later than the pickup date."
                )

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        """Fill rental rate and pickup location from the selected vehicle."""
        if self.vehicle_id:
            self.daily_rate = self.vehicle_id.daily_rate
            self.pickup_location_id = self.vehicle_id.location_id
