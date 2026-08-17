from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CORRUPTED_DATA_DIR = PROJECT_ROOT / "data" / "corrupted"

SEED = 123
CORRUPTION_RATE = 0.01

np.random.seed(SEED)


# ============================================================
# LOAD DATA
# ============================================================

def load_data() -> dict[str, pd.DataFrame]:
    """Load all raw datasets."""

    customers = pd.read_csv(
        RAW_DATA_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )

    destinations = pd.read_csv(
        RAW_DATA_DIR / "destinations.csv",
    )

    bookings = pd.read_csv(
        RAW_DATA_DIR / "bookings.csv",
        parse_dates=[
            "booking_date",
            "departure_date",
            "return_date",
        ],
    )

    payments = pd.read_csv(
        RAW_DATA_DIR / "payments.csv",
        parse_dates=["payment_date"],
    )

    travelers = pd.read_csv(
        RAW_DATA_DIR / "travelers.csv",
    )

    return {
        "customers": customers,
        "destinations": destinations,
        "bookings": bookings,
        "payments": payments,
        "travelers": travelers,
    }


# ============================================================
# CORRUPTION HELPERS
# ============================================================

def corrupt_booking_customer_ids(
    bookings: pd.DataFrame,
    rate: float,
) -> pd.DataFrame:
    """Replace valid customer IDs with invalid IDs."""

    bookings = bookings.copy()

    n_errors = int(len(bookings) * rate)

    indexes = np.random.choice(
        bookings.index,
        size=n_errors,
        replace=False,
    )

    bookings.loc[indexes, "customer_id"] = "C999999"

    return bookings


def corrupt_booking_amounts(
    bookings: pd.DataFrame,
    rate: float,
) -> pd.DataFrame:
    """Introduce negative booking amounts."""

    bookings = bookings.copy()

    n_errors = int(len(bookings) * rate)

    indexes = np.random.choice(
        bookings.index,
        size=n_errors,
        replace=False,
    )

    bookings.loc[indexes, "total_amount"] = -100

    return bookings


def corrupt_booking_dates(
    bookings: pd.DataFrame,
    rate: float,
) -> pd.DataFrame:
    """Introduce invalid booking date relationships."""

    bookings = bookings.copy()

    n_errors = int(len(bookings) * rate)

    indexes = np.random.choice(
        bookings.index,
        size=n_errors,
        replace=False,
    )

    bookings.loc[indexes, "departure_date"] = (
        bookings.loc[indexes, "booking_date"]
        - pd.Timedelta(days=10)
    )

    return bookings


def corrupt_booking_ids(
    bookings: pd.DataFrame,
    rate: float,
) -> pd.DataFrame:
    """Introduce duplicate booking IDs."""

    bookings = bookings.copy()

    n_errors = int(len(bookings) * rate)

    indexes = np.random.choice(
        bookings.index,
        size=n_errors,
        replace=False,
    )

    bookings.loc[indexes, "booking_id"] = (
        bookings.loc[indexes, "booking_id"]
        .iloc[0]
    )

    return bookings


def corrupt_traveler_counts(
    bookings: pd.DataFrame,
    rate: float,
) -> pd.DataFrame:
    """Create inconsistencies between bookings and travelers."""

    bookings = bookings.copy()

    n_errors = int(len(bookings) * rate)

    indexes = np.random.choice(
        bookings.index,
        size=n_errors,
        replace=False,
    )

    bookings.loc[indexes, "travelers"] += 1

    return bookings


def corrupt_payment_amounts(
    payments: pd.DataFrame,
    rate: float,
) -> pd.DataFrame:
    """Create payment amount mismatches."""

    payments = payments.copy()

    n_errors = int(len(payments) * rate)

    indexes = np.random.choice(
        payments.index,
        size=n_errors,
        replace=False,
    )

    payments.loc[indexes, "amount"] *= 0.5

    return payments


# ============================================================
# MAIN CORRUPTION PIPELINE
# ============================================================

def corrupt_data(
    data: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Apply controlled data corruption."""

    data["bookings"] = corrupt_booking_customer_ids(
        data["bookings"],
        CORRUPTION_RATE,
    )

    data["bookings"] = corrupt_booking_amounts(
        data["bookings"],
        CORRUPTION_RATE,
    )

    data["bookings"] = corrupt_booking_dates(
        data["bookings"],
        CORRUPTION_RATE,
    )

    data["bookings"] = corrupt_booking_ids(
        data["bookings"],
        CORRUPTION_RATE,
    )

    data["bookings"] = corrupt_traveler_counts(
        data["bookings"],
        CORRUPTION_RATE,
    )

    data["payments"] = corrupt_payment_amounts(
        data["payments"],
        CORRUPTION_RATE,
    )

    return data


# ============================================================
# SAVE DATA
# ============================================================

def save_data(
    data: dict[str, pd.DataFrame],
) -> None:
    """Save corrupted datasets."""

    for name, dataframe in data.items():
        output_path = CORRUPTED_DATA_DIR / f"{name}.csv"

        dataframe.to_csv(
            output_path,
            index=False,
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run the data corruption pipeline."""

    print("Loading raw data...")

    data = load_data()

    print("Applying controlled data corruption...")

    corrupted_data = corrupt_data(data)

    save_data(corrupted_data)

    print("Data corruption completed.")


if __name__ == "__main__":
    main()