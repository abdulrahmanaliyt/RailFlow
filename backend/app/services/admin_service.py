from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, func

from app.models.user import User
from app.models.train import Train
from app.models.train_schedule import TrainSchedule
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.seat_segment_reservation import SeatSegmentReservation


def get_admin_dashboard_stats(db):

    now = datetime.now(timezone.utc)

    # User statistics
    total_users = db.scalar(
        select(func.count(User.id))
    ) or 0

    # Train statistics
    total_trains = db.scalar(
        select(func.count(Train.id))
    ) or 0

    # Schedule statistics
    total_schedules = db.scalar(
        select(func.count(TrainSchedule.id))
    ) or 0

    upcoming_schedules = db.scalar(
        select(func.count(TrainSchedule.id)).where(
            TrainSchedule.status == "SCHEDULED",
            TrainSchedule.scheduled_departure_at > now,
        )
    ) or 0

    # Booking statistics
    total_bookings = db.scalar(
        select(func.count(Booking.id))
    ) or 0

    confirmed_bookings = db.scalar(
        select(func.count(Booking.id)).where(
            Booking.status == "CONFIRMED"
        )
    ) or 0

    pending_payment_bookings = db.scalar(
        select(func.count(Booking.id)).where(
            Booking.status == "PENDING_PAYMENT"
        )
    ) or 0

    cancelled_bookings = db.scalar(
        select(func.count(Booking.id)).where(
            Booking.status == "CANCELLED"
        )
    ) or 0

    # Payment statistics
    successful_payments = db.scalar(
        select(func.count(Payment.id)).where(
            Payment.status == "SUCCESS"
        )
    ) or 0

    gross_revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "SUCCESS"
        )
    ) or Decimal("0.00")

    # Refund statistics
    successful_refunds = db.scalar(
        select(func.count(Refund.id)).where(
            Refund.status == "SUCCESS"
        )
    ) or 0

    total_refunded = db.scalar(
        select(func.coalesce(func.sum(Refund.amount), 0)).where(
            Refund.status == "SUCCESS"
        )
    ) or Decimal("0.00")

    # Net revenue
    net_revenue = gross_revenue - total_refunded

    # Active seat holds
    active_seat_holds = db.scalar(
        select(func.count(SeatSegmentReservation.id)).where(
            SeatSegmentReservation.status == "HELD",
            SeatSegmentReservation.expires_at > now,
        )
    ) or 0

    # Return result
    return {
        "total_users": total_users,
        "total_trains": total_trains,
        "total_schedules": total_schedules,

        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "pending_payment_bookings": pending_payment_bookings,
        "cancelled_bookings": cancelled_bookings,

        "successful_payments": successful_payments,
        "gross_revenue": gross_revenue,

        "successful_refunds": successful_refunds,
        "total_refunded": total_refunded,
        "net_revenue": net_revenue,

        "active_seat_holds": active_seat_holds,
        "upcoming_schedules": upcoming_schedules,
    }