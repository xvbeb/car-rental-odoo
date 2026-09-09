from odoo import fields, models


class ProductTemplate(models.Model):
    """Розширити товари ознаками додаткової послуги для оренди."""

    _inherit = "product.template"

    is_rental_extra = fields.Boolean(
        string="Додаткова послуга оренди",
        help="Дозволяє вибирати цю послугу в бронюваннях автомобілів.",
    )
    rental_price_per_day = fields.Monetary(
        string="Вартість послуги за добу",
        currency_field="currency_id",
        default=0.0,
    )
