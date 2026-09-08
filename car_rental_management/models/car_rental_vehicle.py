from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalVehicle(models.Model):
    """Зберігати автомобілі, доступні в автопарку прокату."""

    _name = "car.rental.vehicle"
    _description = "Автомобіль для оренди"
    _order = "name, id"

    name = fields.Char(string="Назва", required=True)
    license_plate = fields.Char(string="Державний номер", required=True, index=True)
    vin = fields.Char(string="VIN-код", copy=False)
    category_id = fields.Many2one(
        "car.rental.vehicle.category",
        string="Категорія",
        required=True,
        ondelete="restrict",
    )
    location_id = fields.Many2one(
        "car.rental.location",
        string="Поточний пункт прокату",
        required=True,
        ondelete="restrict",
    )
    daily_rate = fields.Monetary(string="Добовий тариф", required=True, default=0.0)
    currency_id = fields.Many2one(
        "res.currency",
        string="Валюта",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    odometer = fields.Integer(string="Пробіг", default=0)
    state = fields.Selection(
        [
            ("available", "Доступний"),
            ("reserved", "Заброньований"),
            ("rented", "В оренді"),
            ("maintenance", "На обслуговуванні"),
        ],
        string="Статус",
        required=True,
        default="available",
    )
    image_1920 = fields.Image(string="Зображення")
    booking_ids = fields.One2many(
        "car.rental.booking",
        "vehicle_id",
        string="Бронювання",
    )
    inspection_ids = fields.One2many(
        "car.rental.inspection",
        "vehicle_id",
        string="Огляди",
    )
    damage_ids = fields.One2many(
        "car.rental.damage",
        "vehicle_id",
        string="Пошкодження",
    )
    active = fields.Boolean(string="Активний", default=True)

    _license_plate_unique = models.Constraint(
        "UNIQUE(license_plate)",
        "Автомобіль із таким державним номером уже існує.",
    )
    _vin_unique = models.Constraint(
        "UNIQUE(vin)",
        "Автомобіль із таким VIN-кодом уже існує.",
    )

    @api.constrains("daily_rate", "odometer")
    def _check_nonnegative_values(self):
        """Заборонити від'ємні значення тарифу та пробігу."""
        for vehicle in self:
            if vehicle.daily_rate < 0 or vehicle.odometer < 0:
                raise ValidationError(
                    "Добовий тариф і пробіг не можуть бути від'ємними."
                )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        """Підставити стандартний тариф після вибору категорії."""
        if self.category_id:
            self.daily_rate = self.category_id.default_daily_rate
