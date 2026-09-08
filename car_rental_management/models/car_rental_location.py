from odoo import fields, models


class CarRentalLocation(models.Model):
    """Зберігати пункти отримання та повернення автомобілів."""

    _name = "car.rental.location"
    _description = "Пункт прокату автомобілів"
    _order = "name, id"

    name = fields.Char(string="Назва", required=True)
    code = fields.Char(string="Код", required=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Контактна адреса",
        ondelete="restrict",
    )
    phone = fields.Char(string="Телефон")
    email = fields.Char(string="Електронна пошта")
    vehicle_ids = fields.One2many(
        "car.rental.vehicle",
        "location_id",
        string="Автомобілі",
    )
    active = fields.Boolean(string="Активний", default=True)

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "Пункт прокату з таким кодом уже існує.",
    )
