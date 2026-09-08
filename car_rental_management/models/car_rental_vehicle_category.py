from odoo import fields, models


class CarRentalVehicleCategory(models.Model):
    """Класифікувати автомобілі та визначати стандартні умови оренди."""

    _name = "car.rental.vehicle.category"
    _description = "Категорія автомобіля"
    _order = "sequence, name, id"

    name = fields.Char(string="Назва", required=True)
    sequence = fields.Integer(string="Послідовність", default=10)
    default_daily_rate = fields.Monetary(
        string="Стандартний добовий тариф", required=True, default=0.0
    )
    deposit_amount = fields.Monetary(string="Сума застави", default=0.0)
    currency_id = fields.Many2one(
        "res.currency",
        string="Валюта",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    vehicle_ids = fields.One2many(
        "car.rental.vehicle",
        "category_id",
        string="Автомобілі",
    )
    active = fields.Boolean(string="Активна", default=True)

    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "Категорія автомобілів із такою назвою вже існує.",
    )
