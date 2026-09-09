from odoo import api, fields, models


class ResPartner(models.Model):
    """Розширити контакти даними клієнта сервісу оренди автомобілів."""

    _inherit = "res.partner"

    driver_license_number = fields.Char(
        string="Номер посвідчення водія",
        copy=False,
    )
    driver_license_expiry = fields.Date(
        string="Посвідчення водія дійсне до",
    )
    rental_booking_ids = fields.One2many(
        "car.rental.booking",
        "customer_id",
        string="Бронювання автомобілів",
    )
    rental_booking_count = fields.Integer(
        string="Кількість бронювань",
        compute="_compute_rental_booking_count",
    )

    @api.depends("rental_booking_ids")
    def _compute_rental_booking_count(self):
        """Обчислити кількість бронювань для кожного клієнта."""
        for partner in self:
            partner.rental_booking_count = len(partner.rental_booking_ids)

    def action_open_rental_bookings(self):
        """Відкрити всі бронювання вибраного клієнта."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Бронювання клієнта",
            "res_model": "car.rental.booking",
            "view_mode": "list,form,kanban",
            "domain": [("customer_id", "=", self.id)],
            "context": {"default_customer_id": self.id},
        }
