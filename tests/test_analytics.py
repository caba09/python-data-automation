import pandas as pd

from src.analytics import (
    calculate_total_revenue,
    calculate_total_bookings,
    calculate_cancellation_rate,
    calculate_average_booking_value,
)


def test_total_bookings():
    bookings = pd.DataFrame(
        {
            "booking_id": [
                "B001",
                "B002",
                "B003",
            ],
            "status": [
                "CONFIRMED",
                "COMPLETED",
                "CANCELLED",
            ],
            "total_amount": [
                1000,
                2000,
                500,
            ],
        }
    )

    result = calculate_total_bookings(
        bookings
    )

    assert result == 3


def test_total_revenue():
    bookings = pd.DataFrame(
        {
            "status": [
                "CONFIRMED",
                "COMPLETED",
                "CANCELLED",
            ],
            "total_amount": [
                1000,
                2000,
                500,
            ],
        }
    )

    result = calculate_total_revenue(
        bookings
    )

    assert result == 3000


def test_cancellation_rate():
    bookings = pd.DataFrame(
        {
            "status": [
                "CONFIRMED",
                "COMPLETED",
                "CANCELLED",
                "CANCELLED",
            ],
            "total_amount": [
                1000,
                2000,
                500,
                700,
            ],
        }
    )

    result = calculate_cancellation_rate(
        bookings
    )

    assert result == 50.0


def test_average_booking_value():
    bookings = pd.DataFrame(
        {
            "status": [
                "CONFIRMED",
                "COMPLETED",
                "CANCELLED",
            ],
            "total_amount": [
                1000,
                3000,
                500,
            ],
        }
    )

    result = calculate_average_booking_value(
        bookings
    )

    assert result == 2000