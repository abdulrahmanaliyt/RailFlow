
erDiagram
    TRAIN_ROUTES ||--|{ ROUTE_STOPS : contains
    TRAIN_ROUTES ||--|{ ROUTE_SEGMENTS : defines
    ROUTE_STOPS ||--o{ ROUTE_SEGMENTS : starts_or_ends
    TRAIN_ROUTES ||--o{ TRAIN_SCHEDULES : operates
    TRAIN_SCHEDULES ||--o{ BOOKINGS : receives
    ROUTE_STOPS ||--o{ BOOKINGS : boarding_and_destination
    ROUTE_SEGMENTS ||--o{ SEAT_SEGMENT_RESERVATIONS : reserved_on
    TRAIN_SCHEDULES ||--o{ SEAT_SEGMENT_RESERVATIONS : has
    SEATS ||--o{ SEAT_SEGMENT_RESERVATIONS : allocated
    BOOKINGS ||--|{ BOOKING_PASSENGERS : contains
    BOOKING_PASSENGERS ||--o{ SEAT_SEGMENT_RESERVATIONS : assigned
