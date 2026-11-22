from datetime import datetime, timezone
from secrets import token_hex

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.payment import Payment
from app.models.seat_segment_reservation import SeatSegmentReservation


class PaymentValidationError(Exception):
    pass


class PaymentConflictError(Exception):
    pass


def generate_transaction_reference(db: Session) -> str:
    for _ in range(10):
        reference = f"RF-{token_hex(8).upper()}"

        existing = db.scalar(
            select(Payment.id).where(
                Payment.transaction_reference == reference
            )
        )

        if existing is None:
            return reference

    raise PaymentConflictError(
        "Unable to generate transaction reference."
    )


def process_payment(
    db: Session,
    booking_id: int,
    current_user,
    payment_data,
):
    try:
        # 1. Lock booking row to prevent concurrent payment processing.
        booking = db.scalar(
            select(Booking)
            .where(
                Booking.id == booking_id,
                Booking.user_id == current_user.id,
            )
            .with_for_update()
        )

        if booking is None:
            raise PaymentValidationError("Booking not found.")

        # 2. Booking must be awaiting payment.
        if booking.status != "PENDING_PAYMENT":
            raise PaymentConflictError(
                f"Booking cannot be paid. Current status: {booking.status}"
            )

        # 3. Lock all reservations belonging to this booking.
        reservations = db.scalars(
            select(SeatSegmentReservation)
            .where(SeatSegmentReservation.booking_id == booking.id)
            .with_for_update()
        ).all()

        if not reservations:
            raise PaymentValidationError(
                "No seat reservations found for this booking."
            )

        # 4. Verify all holds are still active.
        now = datetime.now(timezone.utc)

        expired = any(
            reservation.status != "HELD"
            or reservation.expires_at is None
            or reservation.expires_at <= now
            for reservation in reservations
        )

        if expired:
            for reservation in reservations:
                if reservation.status == "HELD":
                    reservation.status = "EXPIRED"
                    reservation.expires_at = None

            booking.status = "CANCELLED"
            db.commit()

            raise PaymentConflictError(
                "Your seat hold has expired. Please create a new booking."
            )

        # 5. Create a payment attempt.
        payment = Payment(
            booking_id=booking.id,
            transaction_reference=generate_transaction_reference(db),
            amount=booking.total_amount,
            payment_method=payment_data.payment_method,
            status="INITIATED",
        )

        db.add(payment)
        db.flush()

        # 6. Simulate gateway response.
        if payment_data.simulate_result == "FAILED":
            payment.status = "FAILED"
            db.commit()
            db.refresh(payment)
            return payment

        # 7. Payment successful.
        payment.status = "SUCCESS"
        booking.status = "CONFIRMED"

        for reservation in reservations:
            reservation.status = "CONFIRMED"
            reservation.expires_at = None

        # 8. Save payment + booking + reservations atomically.
        db.commit()
        db.refresh(payment)
        return payment

    except Exception:
        db.rollback()
        raise


def get_payment_history(
    db: Session,
    booking_id: int,
    current_user,
):
    booking = db.scalar(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
    )

    if booking is None:
        raise PaymentValidationError("Booking not found.")

    payments = db.scalars(
        select(Payment)
        .where(Payment.booking_id == booking_id)
        .order_by(Payment.created_at.desc(), Payment.id.desc())
    ).all()

    return {
        "booking_id": booking.id,
        "payments": payments,
    }


def expire_booking_holds(db: Session, schedule_id: int | None = None) -> int:
    now = datetime.now(timezone.utc)

    reservation_query = (
        update(SeatSegmentReservation)
        .where(
            SeatSegmentReservation.status == "HELD",
            SeatSegmentReservation.expires_at <= now,
        )
        .values(
            status="EXPIRED",
            expires_at=None,
        )
    )

    if schedule_id is not None:
        reservation_query = reservation_query.where(
            SeatSegmentReservation.schedule_id == schedule_id
        )

    result = db.execute(reservation_query)

    active_bookings = (
        select(SeatSegmentReservation.booking_id)
        .where(
            SeatSegmentReservation.status == "HELD",
            SeatSegmentReservation.expires_at > now,
        )
    )

    booking_query = (
        update(Booking)
        .where(
            Booking.status == "PENDING_PAYMENT",
            ~Booking.id.in_(active_bookings),
        )
        .values(status="CANCELLED")
    )

    if schedule_id is not None:
        booking_query = booking_query.where(
            Booking.schedule_id == schedule_id
        )

    db.execute(booking_query)

    return result.rowcount