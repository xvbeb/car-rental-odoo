from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalInspection(models.Model):
    """Фіксувати стан автомобіля під час отримання, повернення чи сервісу."""

    _name = "car.rental.inspection"
    _description = "Огляд автомобіля"
    _order = "inspection_datetime desc, id desc"

    name = fields.Char(string="Назва", required=True)
    vehicle_id = fields.Many2one(
        "car.rental.vehicle",
        string="Автомобіль",
        required=True,
        ondelete="cascade",
    )
    booking_id = fields.Many2one(
        "car.rental.booking",
        string="Бронювання",
        ondelete="set null",
    )
    inspection_type = fields.Selection(
        [
            ("pickup", "Під час отримання"),
            ("return", "Під час повернення"),
            ("maintenance", "Технічне обслуговування"),
        ],
        string="Тип огляду",
        required=True,
        default="pickup",
    )
    inspection_datetime = fields.Datetime(
        string="Дата та час огляду",
        required=True,
        default=fields.Datetime.now,
    )
    inspector_id = fields.Many2one(
        "res.users",
        string="Інспектор",
        required=True,
        default=lambda self: self.env.user,
        ondelete="restrict",
    )
    odometer = fields.Integer(string="Пробіг")
    fuel_level = fields.Float(string="Рівень пального, %", default=100.0)
    damage_ids = fields.One2many(
        "car.rental.damage",
        "inspection_id",
        string="Пошкодження",
    )
    notes = fields.Text(string="Примітки")

    @api.constrains("odometer", "fuel_level")
    def _check_measurements(self):
        """Перевірити значення пробігу та рівня пального."""
        for inspection in self:
            if inspection.odometer < 0:
                raise ValidationError("Пробіг не може бути від'ємним.")
            if not 0 <= inspection.fuel_level <= 100:
                raise ValidationError("Рівень пального має бути від 0 до 100 відсотків.")
