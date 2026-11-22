from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from secrets import token_hex

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.booking_passenger import BookingPassenger
from app.models.seat_segment_reservation import SeatSegmentReservation
from app.models.train_schedule import TrainSchedule
from app.models.payment import Payment
from app.models.cancellation import Cancellation
from app.models.refund import Refund


class CancellationValidationError(Exception):
    pass


class CancellationConflictError(Exception):
    pass


def generate_refund_reference(db: Session):
    for _ in range(10):
        reference = f"REF-{token_hex(8).upper()}"

        existing = db.scalar(
            select(Refund.id).where(
                Refund.refund_reference == reference
            )
        )

        if existing is None:
            return reference

    raise CancellationConflictError(
        "Could not generate refund reference."
    )


def get_locked_booking(db: Session, booking_id: int, current_user):
    booking = db.scalar(
        select(Booking)
        .where(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .with_for_update()
    )

    if booking is None:
        raise CancellationValidationError(
            "Booking not found."
        )

    return booking


def validate_cancellation_time(db: Session, booking: Booking):
    schedule = db.get(
        TrainSchedule,
        booking.schedule_id,
    )

    if schedule is None:
        raise CancellationValidationError(
            "Schedule not found."
        )

    departure = schedule.scheduled_departure_at
    if departure is None:
        return

    now = datetime.now(timezone.utc)
    if departure.tzinfo is None:
        departure = departure.replace(
            tzinfo=timezone.utc
        )

    if departure <= now:
        raise CancellationConflictError(
            "Cancellation is not allowed after departure."
        )


def get_successful_payment(db: Session, booking_id: int):
    payment = db.scalar(
        select(Payment)
        .where(
            Payment.booking_id == booking_id,
            Payment.status == "SUCCESS",
        )
        .order_by(Payment.created_at.desc())
    )

    return payment


def calculate_passenger_refund(
    booking: Booking,
    total_passenger_count: int,
) -> Decimal:
    if total_passenger_count <= 0:
        return Decimal("0.00")

    amount = (
        Decimal(str(booking.total_amount))
        / Decimal(total_passenger_count)
    )

    return amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def cancel_one_passenger(
    db: Session,
    booking: Booking,
    passenger: BookingPassenger,
    reason: str | None,
    simulate_refund_result: str,
):
    # Check passenger belongs to booking.
    if passenger.booking_id != booking.id:
        raise CancellationValidationError(
            "Passenger does not belong to this booking."
        )

    # Prevent duplicate cancellations.
    existing = db.scalar(
        select(Cancellation.id).where(
            Cancellation.booking_id == booking.id,
            Cancellation.passenger_id == passenger.id,
        )
    )

    if existing is not None:
        raise CancellationConflictError(
            "Passenger has already been cancelled."
        )

    # Lock this passenger's seat reservations.
    reservations = db.scalars(
        select(SeatSegmentReservation)
        .where(
            SeatSegmentReservation.booking_id == booking.id,
            SeatSegmentReservation.passenger_id == passenger.id,
        )
        .with_for_update()
    ).all()

    if not reservations:
        raise CancellationValidationError(
            "No reservations found for passenger."
        )

    # Release passenger's seats.
    for reservation in reservations:
        if reservation.status not in (
            "HELD",
            "CONFIRMED",
        ):
            raise CancellationConflictError(
                "Passenger's reservation is not active."
            )

        reservation.status = "CANCELLED"
        reservation.expires_at = None

    # Get original passenger count.
    passenger_count = len(
        db.scalars(
            select(BookingPassenger.id).where(
                BookingPassenger.booking_id == booking.id
            )
        ).all()
    )

    # Determine if payment was completed.
    successful_payment = get_successful_payment(
        db,
        booking.id,
    )

    refund_amount = Decimal("0.00")
    refund = None

    if successful_payment is not None:
        refund_amount = calculate_passenger_refund(
            booking,
            passenger_count,
        )

    # Create cancellation record.
    cancellation = Cancellation(
        booking_id=booking.id,
        passenger_id=passenger.id,
        reason=reason,
        refund_amount=refund_amount,
        status="COMPLETED",
    )

    db.add(cancellation)
    db.flush()

    # Simulate refund only if there was successful payment.
    if successful_payment is not None:
        refund = Refund(
            payment_id=successful_payment.id,
            cancellation_id=cancellation.id,
            refund_reference=generate_refund_reference(db),
            amount=refund_amount,
            status="INITIATED",
        )

        db.add(refund)
        db.flush()

        if simulate_refund_result == "SUCCESS":
            refund.status = "SUCCESS"
        else:
            refund.status = "FAILED"

    return cancellation, refund


def cancel_passenger(
    db: Session,
    booking_id: int,
    passenger_id: int,
    current_user,
    cancellation_data,
):
    try:
        booking = get_locked_booking(
            db,
            booking_id,
            current_user,
        )

        if booking.status not in (
            "CONFIRMED",
            "PENDING_PAYMENT",
        ):
            raise CancellationConflictError(
                f"Booking cannot be cancelled. Status: {booking.status}"
            )

        validate_cancellation_time(
            db,
            booking,
        )

        passenger = db.get(
            BookingPassenger,
            passenger_id,
        )

        if passenger is None:
            raise CancellationValidationError(
                "Passenger not found."
            )

        cancellation, refund = cancel_one_passenger(
            db=db,
            booking=booking,
            passenger=passenger,
            reason=cancellation_data.reason,
            simulate_refund_result=(
                cancellation_data.simulate_refund_result
            ),
        )

        # Determine if all passengers are cancelled.
        all_passengers = db.scalars(
            select(BookingPassenger.id).where(
                BookingPassenger.booking_id == booking.id
            )
        ).all()

        cancelled_passengers = db.scalars(
            select(Cancellation.passenger_id).where(
                Cancellation.booking_id == booking.id,
                Cancellation.status == "COMPLETED",
            )
        ).all()

        if set(all_passengers) == set(cancelled_passengers):
            booking.status = "CANCELLED"

        db.commit()

        db.refresh(cancellation)

        if refund is not None:
            db.refresh(refund)

        return cancellation, refund, booking.status

    except (
        CancellationValidationError,
        CancellationConflictError,
    ):
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


def cancel_entire_booking(
    db: Session,
    booking_id: int,
    current_user,
    cancellation_data,
):
    try:
        booking = get_locked_booking(
            db,
            booking_id,
            current_user,
        )

        if booking.status not in (
            "CONFIRMED",
            "PENDING_PAYMENT",
        ):
            raise CancellationConflictError(
                "Booking cannot be cancelled."
            )

        validate_cancellation_time(
            db,
            booking,
        )

        passengers = db.scalars(
            select(BookingPassenger)
            .where(
                BookingPassenger.booking_id == booking.id
            )
            .with_for_update()
        ).all()

        if not passengers:
            raise CancellationValidationError(
                "No passengers found."
            )

        cancellations = []
        refunds = []

        for passenger in passengers:
            existing = db.scalar(
                select(Cancellation.id).where(
                    Cancellation.booking_id == booking.id,
                    Cancellation.passenger_id == passenger.id,
                )
            )

            if existing is not None:
                continue

            cancellation, refund = cancel_one_passenger(
                db=db,
                booking=booking,
                passenger=passenger,
                reason=cancellation_data.reason,
                simulate_refund_result=(
                    cancellation_data.simulate_refund_result
                ),
            )

            cancellations.append(cancellation)

            if refund is not None:
                refunds.append(refund)

        booking.status = "CANCELLED"

        db.commit()

        for cancellation in cancellations:
            db.refresh(cancellation)

        for refund in refunds:
            db.refresh(refund)

        return booking, cancellations, refunds

    except (
        CancellationValidationError,
        CancellationConflictError,
    ):
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise