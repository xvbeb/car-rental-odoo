from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalBooking(models.Model):
    """Керувати бронюваннями клієнтів та активною орендою автомобілів."""

    _name = "car.rental.booking"
    _description = "Бронювання автомобіля"
    _order = "date_from desc, id desc"

    name = fields.Char(string="Номер", required=True, default="Нове", copy=False)
    customer_id = fields.Many2one(
        "res.partner",
        string="Клієнт",
        required=True,
        ondelete="restrict",
    )
    vehicle_id = fields.Many2one(
        "car.rental.vehicle",
        string="Автомобіль",
        required=True,
        ondelete="restrict",
    )
    pickup_location_id = fields.Many2one(
        "car.rental.location",
        string="Пункт отримання",
        required=True,
        ondelete="restrict",
    )
    return_location_id = fields.Many2one(
        "car.rental.location",
        string="Пункт повернення",
        required=True,
        ondelete="restrict",
    )
    date_from = fields.Datetime(
        string="Дата та час отримання", required=True, default=fields.Datetime.now
    )
    date_to = fields.Datetime(string="Дата та час повернення", required=True)
    day_count = fields.Integer(
        string="Кількість днів", compute="_compute_amounts", store=True
    )
    daily_rate = fields.Monetary(string="Добовий тариф", required=True)
    extra_service_ids = fields.Many2many(
        "product.product",
        "car_rental_booking_product_rel",
        "booking_id",
        "product_id",
        string="Додаткові послуги",
        domain=[("is_rental_extra", "=", True)],
    )
    extra_services_amount = fields.Monetary(
        string="Вартість додаткових послуг",
        compute="_compute_amounts",
        store=True,
    )
    total_amount = fields.Monetary(
        string="Загальна сума", compute="_compute_amounts", store=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Валюта",
        related="vehicle_id.currency_id",
        store=True,
    )
    state = fields.Selection(
        [
            ("draft", "Чернетка"),
            ("confirmed", "Підтверджено"),
            ("active", "Активна"),
            ("done", "Завершено"),
            ("cancelled", "Скасовано"),
        ],
        string="Статус",
        required=True,
        default="draft",
    )
    inspection_ids = fields.One2many(
        "car.rental.inspection",
        "booking_id",
        string="Огляди",
    )
    notes = fields.Text(string="Примітки")

    @api.depends(
        "date_from",
        "date_to",
        "daily_rate",
        "extra_service_ids.rental_price_per_day",
    )
    def _compute_amounts(self):
        """Обчислити кількість оплачуваних днів і загальну суму."""
        for booking in self:
            if booking.date_from and booking.date_to:
                seconds = (booking.date_to - booking.date_from).total_seconds()
                booking.day_count = max(1, int((seconds + 86399) // 86400))
            else:
                booking.day_count = 0
            services_daily_rate = sum(
                booking.extra_service_ids.mapped("rental_price_per_day")
            )
            booking.extra_services_amount = booking.day_count * services_daily_rate
            booking.total_amount = (
                booking.day_count * booking.daily_rate
                + booking.extra_services_amount
            )

    @api.constrains("date_from", "date_to")
    def _check_rental_period(self):
        """Перевірити, що повернення відбувається пізніше за отримання."""
        for booking in self:
            if booking.date_from and booking.date_to <= booking.date_from:
                raise ValidationError(
                    "Дата повернення має бути пізнішою за дату отримання."
                )

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        """Заповнити тариф і пункт отримання з вибраного автомобіля."""
        if self.vehicle_id:
            self.daily_rate = self.vehicle_id.daily_rate
            self.pickup_location_id = self.vehicle_id.location_id
