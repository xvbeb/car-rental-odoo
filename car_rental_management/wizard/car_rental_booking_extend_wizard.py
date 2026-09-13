from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class CarRentalBookingExtendWizard(models.TransientModel):
    """Тимчасовий майстер для зміни строку вибраних бронювань."""

    _name = "car.rental.booking.extend.wizard"
    _description = "Зміна дати повернення автомобіля"

    booking_ids = fields.Many2many(
        "car.rental.booking",
        string="Бронювання",
        required=True,
        readonly=True,
    )
    new_date_to = fields.Datetime(
        string="Нова дата та час повернення",
        required=True,
    )

    @api.model
    def default_get(self, field_names):
        """Додати до майстра бронювання, вибрані в активному вікні."""
        values = super().default_get(field_names)
        if self.env.context.get("active_model") == "car.rental.booking":
            booking_ids = self.env.context.get("active_ids", [])
            values["booking_ids"] = [(6, 0, booking_ids)]
            bookings = self.env["car.rental.booking"].browse(booking_ids)
            if bookings:
                values["new_date_to"] = max(bookings.mapped("date_to"))
        return values

    def action_apply(self):
        """Записати нову дату повернення у вибрані активні бронювання."""
        self.ensure_one()
        if not self.booking_ids:
            raise UserError("Виберіть хоча б одне бронювання.")

        closed_bookings = self.booking_ids.filtered(
            lambda booking: booking.state in ("done", "cancelled")
        )
        if closed_bookings:
            raise UserError(
                "Не можна змінити строк завершених або скасованих бронювань."
            )

        invalid_bookings = self.booking_ids.filtered(
            lambda booking: self.new_date_to <= booking.date_from
        )
        if invalid_bookings:
            raise ValidationError(
                "Нова дата повернення має бути пізнішою за дату отримання."
            )

        self.booking_ids.write({"date_to": self.new_date_to})
        return {"type": "ir.actions.act_window_close"}
