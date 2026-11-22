from decimal import Decimal

from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_trains: int
    total_schedules: int

    total_bookings: int
    confirmed_bookings: int
    pending_payment_bookings: int
    cancelled_bookings: int

    successful_payments: int
    gross_revenue: Decimal

    successful_refunds: int
    total_refunded: Decimal
    net_revenue: Decimal

    active_seat_holds: int
    upcoming_schedules: int