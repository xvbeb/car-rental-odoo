from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CarRentalDamage(models.Model):
    """Обліковувати пошкодження, виявлені на автомобілях прокату."""

    _name = "car.rental.damage"
    _description = "Пошкодження автомобіля"
    _order = "detected_date desc, id desc"

    name = fields.Char(string="Назва", required=True)
    vehicle_id = fields.Many2one(
        "car.rental.vehicle",
        string="Автомобіль",
        required=True,
        ondelete="cascade",
    )
    inspection_id = fields.Many2one(
        "car.rental.inspection",
        string="Огляд",
        ondelete="set null",
    )
    detected_date = fields.Date(
        string="Дата виявлення", required=True, default=fields.Date.context_today
    )
    severity = fields.Selection(
        [("minor", "Незначне"), ("medium", "Середнє"), ("major", "Серйозне")],
        string="Серйозність",
        required=True,
        default="minor",
    )
    state = fields.Selection(
        [("reported", "Зафіксовано"), ("repairing", "Ремонтується"), ("fixed", "Усунено")],
        string="Статус",
        required=True,
        default="reported",
    )
    repair_cost = fields.Monetary(string="Вартість ремонту", default=0.0)
    currency_id = fields.Many2one(
        "res.currency",
        string="Валюта",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Text(string="Опис")
    image = fields.Image(string="Зображення")

    @api.constrains("repair_cost")
    def _check_repair_cost(self):
        """Заборонити від'ємну очікувану або фактичну вартість ремонту."""
        for damage in self:
            if damage.repair_cost < 0:
                raise ValidationError("Вартість ремонту не може бути від'ємною.")
