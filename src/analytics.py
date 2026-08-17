from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"


# ============================================================
# DATA LOADING
# ============================================================

def load_analytics_data() -> dict[str, pd.DataFrame]:
    """Load clean datasets used for business analytics."""

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

    return {
        "customers": customers,
        "destinations": destinations,
        "bookings": bookings,
    }


# ============================================================
# KPI CALCULATIONS
# ============================================================

def calculate_total_revenue(
    bookings: pd.DataFrame,
) -> float:
    """Calculate revenue from completed and confirmed bookings."""

    valid_bookings = bookings[
        bookings["status"].isin(
            ["CONFIRMED", "COMPLETED"]
        )
    ]

    return float(
        valid_bookings["total_amount"].sum()
    )


def calculate_total_bookings(
    bookings: pd.DataFrame,
) -> int:
    """Calculate the number of bookings."""

    return int(len(bookings))


def calculate_average_booking_value(
    bookings: pd.DataFrame,
) -> float:
    """Calculate the average booking value."""

    valid_bookings = bookings[
        bookings["status"].isin(
            ["CONFIRMED", "COMPLETED"]
        )
    ]

    return float(
        valid_bookings["total_amount"].mean()
    )


def calculate_cancellation_rate(
    bookings: pd.DataFrame,
) -> float:
    """Calculate the percentage of cancelled bookings."""

    return float(
        (
            bookings["status"] == "CANCELLED"
        ).mean()
        * 100
    )


def calculate_average_trip_duration(
    bookings: pd.DataFrame,
) -> float:
    """Calculate the average trip duration in days."""

    duration = (
        bookings["return_date"]
        - bookings["departure_date"]
    ).dt.days

    return float(duration.mean())


# ============================================================
# CUSTOMER ANALYTICS
# ============================================================

def calculate_unique_customers(
    customers: pd.DataFrame,
) -> int:
    """Calculate the number of customers."""

    return int(
        customers["customer_id"].nunique()
    )


def calculate_revenue_by_segment(
    bookings: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revenue by customer segment."""

    valid_bookings = bookings[
        bookings["status"].isin(
            ["CONFIRMED", "COMPLETED"]
        )
    ]

    merged = valid_bookings.merge(
        customers[
            [
                "customer_id",
                "customer_segment",
            ]
        ],
        on="customer_id",
        how="left",
    )

    result = (
        merged
        .groupby("customer_segment")["total_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "total_amount",
            ascending=False,
        )
    )

    return result


# ============================================================
# DESTINATION ANALYTICS
# ============================================================

def calculate_revenue_by_destination(
    bookings: pd.DataFrame,
    destinations: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revenue by destination."""

    valid_bookings = bookings[
        bookings["status"].isin(
            ["CONFIRMED", "COMPLETED"]
        )
    ]

    merged = valid_bookings.merge(
        destinations,
        on="destination_id",
        how="left",
    )

    result = (
        merged
        .groupby(
            [
                "destination_id",
                "city",
                "country",
            ]
        )["total_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "total_amount",
            ascending=False,
        )
    )

    return result


def calculate_bookings_by_destination(
    bookings: pd.DataFrame,
    destinations: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate booking volume by destination."""

    merged = bookings.merge(
        destinations,
        on="destination_id",
        how="left",
    )

    result = (
        merged
        .groupby(
            [
                "destination_id",
                "city",
                "country",
            ]
        )
        .size()
        .reset_index(name="bookings")
        .sort_values(
            "bookings",
            ascending=False,
        )
    )

    return result


# ============================================================
# CHANNEL ANALYTICS
# ============================================================

def calculate_revenue_by_channel(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revenue by booking channel."""

    valid_bookings = bookings[
        bookings["status"].isin(
            ["CONFIRMED", "COMPLETED"]
        )
    ]

    result = (
        valid_bookings
        .groupby("booking_channel")["total_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "total_amount",
            ascending=False,
        )
    )

    return result


# ============================================================
# MONTHLY ANALYTICS
# ============================================================

def calculate_monthly_revenue(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly revenue."""

    valid_bookings = bookings[
        bookings["status"].isin(
            ["CONFIRMED", "COMPLETED"]
        )
    ].copy()

    valid_bookings["month"] = (
        valid_bookings["booking_date"]
        .dt.to_period("M")
        .astype(str)
    )

    result = (
        valid_bookings
        .groupby("month")["total_amount"]
        .sum()
        .reset_index()
    )

    return result


# ============================================================
# ANALYTICS PIPELINE
# ============================================================

def run_analytics(
    data: dict[str, pd.DataFrame],
) -> dict[str, object]:
    """Calculate all business KPIs."""

    customers = data["customers"]
    destinations = data["destinations"]
    bookings = data["bookings"]

    kpis = {
        "total_revenue": calculate_total_revenue(
            bookings
        ),
        "total_bookings": calculate_total_bookings(
            bookings
        ),
        "unique_customers": calculate_unique_customers(
            customers
        ),
        "average_booking_value": calculate_average_booking_value(
            bookings
        ),
        "cancellation_rate": calculate_cancellation_rate(
            bookings
        ),
        "average_trip_duration": calculate_average_trip_duration(
            bookings
        ),
    }

    tables = {
        "revenue_by_segment": calculate_revenue_by_segment(
            bookings,
            customers,
        ),
        "revenue_by_destination": calculate_revenue_by_destination(
            bookings,
            destinations,
        ),
        "bookings_by_destination": calculate_bookings_by_destination(
            bookings,
            destinations,
        ),
        "revenue_by_channel": calculate_revenue_by_channel(
            bookings
        ),
        "monthly_revenue": calculate_monthly_revenue(
            bookings
        ),
    }

    return {
        "kpis": kpis,
        "tables": tables,
    }


# ============================================================
# CONSOLE OUTPUT
# ============================================================

def print_summary(
    results: dict[str, object],
) -> None:
    """Print the main analytics summary."""

    kpis = results["kpis"]

    print("\n" + "=" * 70)
    print("TRIPPULSE BUSINESS ANALYTICS")
    print("=" * 70)

    print(
        f"Total revenue: "
        f"€{kpis['total_revenue']:,.2f}"
    )

    print(
        f"Total bookings: "
        f"{kpis['total_bookings']:,}"
    )

    print(
        f"Unique customers: "
        f"{kpis['unique_customers']:,}"
    )

    print(
        f"Average booking value: "
        f"€{kpis['average_booking_value']:,.2f}"
    )

    print(
        f"Cancellation rate: "
        f"{kpis['cancellation_rate']:.2f}%"
    )

    print(
        f"Average trip duration: "
        f"{kpis['average_trip_duration']:.2f} days"
    )

    print("\n" + "-" * 70)
    print("TOP 10 DESTINATIONS BY REVENUE")
    print("-" * 70)

    print(
        results["tables"]["revenue_by_destination"]
        .head(10)
        .to_string(index=False)
    )

    print("\n" + "-" * 70)
    print("REVENUE BY CUSTOMER SEGMENT")
    print("-" * 70)

    print(
        results["tables"]["revenue_by_segment"]
        .to_string(index=False)
    )

    print("\n" + "-" * 70)
    print("REVENUE BY CHANNEL")
    print("-" * 70)

    print(
        results["tables"]["revenue_by_channel"]
        .to_string(index=False)
    )

    print("=" * 70)


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    results: dict[str, object],
) -> None:
    """Save analytics results to CSV files."""

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    kpis = pd.DataFrame(
        [
            {
                "metric": key,
                "value": value,
            }
            for key, value
            in results["kpis"].items()
        ]
    )

    kpis.to_csv(
        REPORTS_DIR / "business_kpis.csv",
        index=False,
    )

    for name, dataframe in results["tables"].items():
        dataframe.to_csv(
            REPORTS_DIR / f"{name}.csv",
            index=False,
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run the TripPulse analytics pipeline."""

    print("Loading clean data...")

    data = load_analytics_data()

    print("Calculating business KPIs...")

    results = run_analytics(data)

    print_summary(results)

    save_results(results)

    print("\nAnalytics reports saved successfully.")


if __name__ == "__main__":
    main()