from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

SEED = 42

fake = Faker()
Faker.seed(SEED)
np.random.seed(SEED)


# ============================================================
# DESTINATIONS
# ============================================================

def generate_destinations(n: int = 50) -> pd.DataFrame:
    """Generate a synthetic destinations dataset."""

    predefined_destinations = [
        ("D001", "Tokyo", "Japan", "Asia"),
        ("D002", "Rome", "Italy", "Europe"),
        ("D003", "Paris", "France", "Europe"),
        ("D004", "New York", "USA", "North America"),
        ("D005", "Bangkok", "Thailand", "Asia"),
        ("D006", "Barcelona", "Spain", "Europe"),
        ("D007", "Reykjavik", "Iceland", "Europe"),
        ("D008", "Cape Town", "South Africa", "Africa"),
        ("D009", "Sydney", "Australia", "Oceania"),
        ("D010", "Cancun", "Mexico", "North America"),
    ]

    rows = []

    for i in range(n):
        if i < len(predefined_destinations):
            destination_id, city, country, continent = predefined_destinations[i]

        else:
            destination_id = f"D{i + 1:03d}"
            city = fake.city()
            country = fake.country()
            continent = fake.random_element(
                elements=[
                    "Europe",
                    "Asia",
                    "North America",
                    "South America",
                    "Africa",
                    "Oceania",
                ]
            )

        rows.append(
            {
                "destination_id": destination_id,
                "city": city,
                "country": country,
                "continent": continent,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# CUSTOMERS
# ============================================================

def generate_customers(n: int = 5000) -> pd.DataFrame:
    """Generate a synthetic customers dataset."""

    segments = [
        "Standard",
        "Premium",
        "Business",
    ]

    rows = []

    for i in range(n):
        rows.append(
            {
                "customer_id": f"C{i + 1:05d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "country": fake.country(),
                "signup_date": fake.date_between(
                    start_date="-3y",
                    end_date="today",
                ),
                "customer_segment": np.random.choice(
                    segments,
                    p=[0.70, 0.25, 0.05],
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# BOOKINGS
# ============================================================

def generate_bookings(
    customers: pd.DataFrame,
    destinations: pd.DataFrame,
    n: int = 25000,
) -> pd.DataFrame:
    """Generate a synthetic bookings dataset."""

    booking_ids = [
        f"B{i + 1:06d}"
        for i in range(n)
    ]

    customer_ids = np.random.choice(
        customers["customer_id"],
        size=n,
    )

    destination_ids = np.random.choice(
        destinations["destination_id"],
        size=n,
    )

    booking_dates = pd.to_datetime(
        np.random.choice(
            pd.date_range(
                "2025-01-01",
                "2026-06-30",
            ),
            size=n,
        )
    )

    trip_durations = np.random.randint(
        3,
        15,
        size=n,
    )

    departure_dates = booking_dates + pd.to_timedelta(
        np.random.randint(
            7,
            180,
            size=n,
        ),
        unit="D",
    )

    return_dates = departure_dates + pd.to_timedelta(
        trip_durations,
        unit="D",
    )

    travelers = np.random.choice(
        [1, 2, 3, 4, 5],
        size=n,
        p=[0.10, 0.45, 0.25, 0.15, 0.05],
    )

    booking_channels = np.random.choice(
        ["WEB", "MOBILE", "AGENCY"],
        size=n,
        p=[0.55, 0.30, 0.15],
    )

    statuses = np.random.choice(
        ["CONFIRMED", "CANCELLED", "COMPLETED"],
        size=n,
        p=[0.60, 0.10, 0.30],
    )

    base_prices = np.random.uniform(
        300,
        2500,
        size=n,
    )

    total_amount = (
        base_prices
        * trip_durations
        * travelers
        / 5
    )

    total_amount = np.round(
        total_amount,
        2,
    )

    return pd.DataFrame(
        {
            "booking_id": booking_ids,
            "customer_id": customer_ids,
            "destination_id": destination_ids,
            "booking_date": booking_dates,
            "departure_date": departure_dates,
            "return_date": return_dates,
            "travelers": travelers,
            "total_amount": total_amount,
            "currency": "EUR",
            "booking_channel": booking_channels,
            "status": statuses,
        }
    )

# ============================================================
# PAYMENTS
# ============================================================

def generate_payments(bookings: pd.DataFrame) -> pd.DataFrame:
    """Generate a synthetic payments dataset from bookings."""

    payment_rows = []

    payment_id = 1

    for _, booking in bookings.iterrows():
        booking_id = booking["booking_id"]
        booking_amount = booking["total_amount"]
        booking_status = booking["status"]

        # Cancelled bookings do not generate a payment.
        if booking_status == "CANCELLED":
            continue

        # Most bookings are paid in a single transaction.
        payment_method = np.random.choice(
            ["CREDIT_CARD", "PAYPAL", "BANK_TRANSFER"],
            p=[0.60, 0.25, 0.15],
        )

        payment_rows.append(
            {
                "payment_id": f"P{payment_id:07d}",
                "booking_id": booking_id,
                "payment_date": booking["booking_date"],
                "amount": booking_amount,
                "payment_method": payment_method,
                "payment_status": "COMPLETED",
            }
        )

        payment_id += 1

    return pd.DataFrame(payment_rows)

# ============================================================
# TRAVELERS
# ============================================================

def generate_travelers(bookings: pd.DataFrame) -> pd.DataFrame:
    """Generate travelers linked to bookings."""

    traveler_rows = []

    traveler_id = 1

    for _, booking in bookings.iterrows():
        booking_id = booking["booking_id"]
        number_of_travelers = booking["travelers"]

        for _ in range(number_of_travelers):
            traveler_rows.append(
                {
                    "traveler_id": f"T{traveler_id:07d}",
                    "booking_id": booking_id,
                    "age": np.random.randint(18, 76),
                    "gender": np.random.choice(
                        ["F", "M", "X"],
                        p=[0.48, 0.48, 0.04],
                    ),
                    "traveler_type": np.random.choice(
                        ["ADULT", "SENIOR"],
                        p=[0.85, 0.15],
                    ),
                }
            )

            traveler_id += 1

    return pd.DataFrame(traveler_rows)

# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Generate all synthetic raw datasets."""

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destinations = generate_destinations()
    customers = generate_customers()

    bookings = generate_bookings(
        customers,
        destinations,
    )
    payments = generate_payments(bookings)
    travelers = generate_travelers(bookings)

    destinations.to_csv(
        DATA_DIR / "destinations.csv",
        index=False,
    )

    customers.to_csv(
        DATA_DIR / "customers.csv",
        index=False,
    )

    bookings.to_csv(
        DATA_DIR / "bookings.csv",
        index=False,
    )
    payments.to_csv(
        DATA_DIR / "payments.csv",
        index=False,
    )

    travelers.to_csv(
        DATA_DIR / "travelers.csv",
        index=False,
    )

    print(f"Generated {len(destinations)} destinations")
    print(f"Generated {len(customers)} customers")
    print(f"Generated {len(bookings)} bookings")
    print(f"Generated {len(payments)} payments")
    print(f"Generated {len(travelers)} travelers")

if __name__ == "__main__":
    main()