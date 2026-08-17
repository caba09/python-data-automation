git push origin mainimport pandas as pd

from src.data_quality import (
    check_duplicate_ids,
    check_missing_values,
    check_foreign_keys,
    check_invalid_booking_dates,
    check_invalid_booking_amounts,
    check_invalid_traveler_counts,
    check_traveler_counts,
    check_payment_amounts,
    run_quality_checks
)


# ============================================================
# UNIQUENESS
# ============================================================

def test_duplicate_ids():
    df = pd.DataFrame(
        {
            "customer_id": [
                "C001",
                "C002",
                "C002",
                "C003",
            ]
        }
    )

    result = check_duplicate_ids(
        df,
        "customer_id",
    )

    assert result == 1


# ============================================================
# COMPLETENESS
# ============================================================

def test_missing_values():
    df = pd.DataFrame(
        {
            "customer_id": [
                "C001",
                None,
                "C003",
            ],
            "country": [
                "Italy",
                "France",
                None,
            ],
        }
    )

    result = check_missing_values(
        df
    )

    assert result == 2


# ============================================================
# REFERENTIAL INTEGRITY
# ============================================================

def test_foreign_keys():
    customers = pd.DataFrame(
        {
            "customer_id": [
                "C001",
                "C002",
            ]
        }
    )

    bookings = pd.DataFrame(
        {
            "customer_id": [
                "C001",
                "C002",
                "C999",
            ]
        }
    )

    result = check_foreign_keys(
        bookings,
        "customer_id",
        customers,
        "customer_id",
    )

    assert result == 1


# ============================================================
# BOOKING DATES
# ============================================================

def test_invalid_booking_dates():
    bookings = pd.DataFrame(
        {
            "booking_date": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-02-01",
                ]
            ),
            "departure_date": pd.to_datetime(
                [
                    "2025-01-10",
                    "2025-01-20",
                ]
            ),
            "return_date": pd.to_datetime(
                [
                    "2025-01-15",
                    "2025-01-10",
                ]
            ),
        }
    )

    result = check_invalid_booking_dates(
        bookings
    )

    assert result == 1


# ============================================================
# BOOKING AMOUNTS
# ============================================================

def test_invalid_booking_amounts():
    bookings = pd.DataFrame(
        {
            "total_amount": [
                1000,
                500,
                0,
                -100,
            ]
        }
    )

    result = check_invalid_booking_amounts(
        bookings
    )

    assert result == 2


# ============================================================
# TRAVELER COUNTS
# ============================================================

def test_invalid_traveler_counts():
    bookings = pd.DataFrame(
        {
            "travelers": [
                1,
                5,
                20,
                0,
                21,
            ]
        }
    )

    result = check_invalid_traveler_counts(
        bookings
    )

    assert result == 2


# ============================================================
# TRAVELER CONSISTENCY
# ============================================================

def test_traveler_count_mismatch():
    bookings = pd.DataFrame(
        {
            "booking_id": [
                "B001",
                "B002",
            ],
            "travelers": [
                2,
                3,
            ],
        }
    )

    travelers = pd.DataFrame(
        {
            "booking_id": [
                "B001",
                "B001",
                "B002",
            ]
        }
    )

    result = check_traveler_counts(
        bookings,
        travelers,
    )

    assert result == 1


# ============================================================
# PAYMENT CONSISTENCY
# ============================================================

def test_payment_amount_mismatch():
    bookings = pd.DataFrame(
        {
            "booking_id": [
                "B001",
                "B002",
            ],
            "total_amount": [
                1000,
                2000,
            ],
            "status": [
                "CONFIRMED",
                "CANCELLED",
            ],
        }
    )

    payments = pd.DataFrame(
        {
            "booking_id": [
                "B001",
                "B002",
            ],
            "amount": [
                900,
                2000,
            ],
        }
    )

    result = check_payment_amounts(
        bookings,
        payments,
    )

    assert result == 1

def test_run_quality_checks_detects_errors():
    customers = pd.DataFrame(
        {
            "customer_id": [
                "C001",
                "C002",
            ]
        }
    )

    destinations = pd.DataFrame(
        {
            "destination_id": [
                "D001",
                "D002",
            ]
        }
    )

    bookings = pd.DataFrame(
        {
            "booking_id": [
                "B001",
                "B001",
            ],
            "customer_id": [
                "C001",
                "C999",
            ],
            "destination_id": [
                "D001",
                "D002",
            ],
            "booking_date": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                ]
            ),
            "departure_date": pd.to_datetime(
                [
                    "2025-01-10",
                    "2025-01-10",
                ]
            ),
            "return_date": pd.to_datetime(
                [
                    "2025-01-15",
                    "2025-01-15",
                ]
            ),
            "total_amount": [
                1000,
                2000,
            ],
            "travelers": [
                2,
                2,
            ],
            "status": [
                "CONFIRMED",
                "CONFIRMED",
            ],
        }
    )

    payments = pd.DataFrame(
        {
            "payment_id": [
                "P001",
                "P002",
            ],
            "booking_id": [
                "B001",
                "B001",
            ],
            "amount": [
                1000,
                2000,
            ],
        }
    )

    travelers = pd.DataFrame(
        {
            "traveler_id": [
                "T001",
                "T002",
                "T003",
            ],
            "booking_id": [
                "B001",
                "B001",
                "B002",
            ],
        }
    )

    data = {
        "customers": customers,
        "destinations": destinations,
        "bookings": bookings,
        "payments": payments,
        "travelers": travelers,
    }

    result = run_quality_checks(data)

    # The duplicated booking ID should be detected.
    duplicate_booking_check = result[
        result["check"]
        == "Duplicate booking IDs"
    ]

    assert duplicate_booking_check.iloc[0]["errors"] == 1

    assert (
        duplicate_booking_check.iloc[0]["status"]
        == "FAIL"
    )

    # The invalid customer reference C999
    # should also be detected.
    invalid_customer_check = result[
        result["check"]
        == "Invalid booking customer IDs"
    ]

    assert invalid_customer_check.iloc[0]["errors"] == 1

    assert (
        invalid_customer_check.iloc[0]["status"]
        == "FAIL"
    )