from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
#DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR = PROJECT_ROOT / "data" / "corrupted"
REPORTS_DIR = PROJECT_ROOT / "reports"


# ============================================================
# DATA LOADING
# ============================================================

def load_data() -> dict[str, pd.DataFrame]:
    """Load all raw datasets."""

    customers = pd.read_csv(
        DATA_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )

    destinations = pd.read_csv(
        DATA_DIR / "destinations.csv",
    )

    bookings = pd.read_csv(
        DATA_DIR / "bookings.csv",
        parse_dates=[
            "booking_date",
            "departure_date",
            "return_date",
        ],
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv",
        parse_dates=["payment_date"],
    )

    travelers = pd.read_csv(
        DATA_DIR / "travelers.csv",
    )

    return {
        "customers": customers,
        "destinations": destinations,
        "bookings": bookings,
        "payments": payments,
        "travelers": travelers,
    }


# ============================================================
# CHECK HELPERS
# ============================================================

def check_duplicate_ids(
    df: pd.DataFrame,
    column: str,
) -> int:
    """Return the number of duplicated IDs."""

    return int(df[column].duplicated().sum())


def check_missing_values(
    df: pd.DataFrame,
) -> int:
    """Return the total number of missing values."""

    return int(df.isna().sum().sum())


# ============================================================
# REFERENTIAL INTEGRITY
# ============================================================

def check_foreign_keys(
    child_df: pd.DataFrame,
    child_column: str,
    parent_df: pd.DataFrame,
    parent_column: str,
) -> int:
    """Count child records referencing missing parent IDs."""

    valid_parent_ids = set(parent_df[parent_column])

    invalid_references = ~child_df[child_column].isin(
        valid_parent_ids
    )

    return int(invalid_references.sum())


# ============================================================
# BOOKING VALIDATION
# ============================================================

def check_invalid_booking_dates(
    bookings: pd.DataFrame,
) -> int:
    """Count bookings with invalid date relationships."""

    invalid_dates = (
        (bookings["departure_date"] < bookings["booking_date"])
        | (bookings["return_date"] < bookings["departure_date"])
    )

    return int(invalid_dates.sum())


def check_invalid_booking_amounts(
    bookings: pd.DataFrame,
) -> int:
    """Count bookings with non-positive amounts."""

    invalid_amounts = bookings["total_amount"] <= 0

    return int(invalid_amounts.sum())


def check_invalid_traveler_counts(
    bookings: pd.DataFrame,
) -> int:
    """Count bookings with invalid traveler counts."""

    invalid_travelers = (
        (bookings["travelers"] < 1)
        | (bookings["travelers"] > 20)
    )

    return int(invalid_travelers.sum())


# ============================================================
# TRAVELER VALIDATION
# ============================================================

def check_traveler_counts(
    bookings: pd.DataFrame,
    travelers: pd.DataFrame,
) -> int:
    """Compare declared and actual traveler counts."""

    actual_counts = (
        travelers
        .groupby("booking_id")
        .size()
        .rename("actual_travelers")
    )

    comparison = bookings[
        ["booking_id", "travelers"]
    ].merge(
        actual_counts,
        on="booking_id",
        how="left",
    )

    comparison["actual_travelers"] = (
        comparison["actual_travelers"]
        .fillna(0)
    )

    mismatches = (
        comparison["travelers"]
        != comparison["actual_travelers"]
    )

    return int(mismatches.sum())


# ============================================================
# PAYMENT VALIDATION
# ============================================================

def check_payment_amounts(
    bookings: pd.DataFrame,
    payments: pd.DataFrame,
) -> int:
    """Compare booking amounts with payment totals."""

    payment_totals = (
        payments
        .groupby("booking_id")["amount"]
        .sum()
        .rename("paid_amount")
    )

    comparison = bookings[
        ["booking_id", "total_amount", "status"]
    ].merge(
        payment_totals,
        on="booking_id",
        how="left",
    )

    comparison["paid_amount"] = (
        comparison["paid_amount"]
        .fillna(0)
    )

    non_cancelled = comparison["status"] != "CANCELLED"

    mismatches = (
        non_cancelled
        & (
            comparison["total_amount"]
            .round(2)
            != comparison["paid_amount"]
            .round(2)
        )
    )

    return int(mismatches.sum())


# ============================================================
# QUALITY REPORT
# ============================================================

def run_quality_checks(
    data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Run all data quality checks."""

    customers = data["customers"]
    destinations = data["destinations"]
    bookings = data["bookings"]
    payments = data["payments"]
    travelers = data["travelers"]

    checks = [
        {
            "check": "Duplicate customer IDs",
            "category": "Uniqueness",
            "errors": check_duplicate_ids(
                customers,
                "customer_id",
            ),
        },
        {
            "check": "Duplicate destination IDs",
            "category": "Uniqueness",
            "errors": check_duplicate_ids(
                destinations,
                "destination_id",
            ),
        },
        {
            "check": "Duplicate booking IDs",
            "category": "Uniqueness",
            "errors": check_duplicate_ids(
                bookings,
                "booking_id",
            ),
        },
        {
            "check": "Duplicate payment IDs",
            "category": "Uniqueness",
            "errors": check_duplicate_ids(
                payments,
                "payment_id",
            ),
        },
        {
            "check": "Duplicate traveler IDs",
            "category": "Uniqueness",
            "errors": check_duplicate_ids(
                travelers,
                "traveler_id",
            ),
        },
        {
            "check": "Missing customer values",
            "category": "Completeness",
            "errors": check_missing_values(customers),
        },
        {
            "check": "Missing destination values",
            "category": "Completeness",
            "errors": check_missing_values(destinations),
        },
        {
            "check": "Missing booking values",
            "category": "Completeness",
            "errors": check_missing_values(bookings),
        },
        {
            "check": "Missing payment values",
            "category": "Completeness",
            "errors": check_missing_values(payments),
        },
        {
            "check": "Missing traveler values",
            "category": "Completeness",
            "errors": check_missing_values(travelers),
        },
        {
            "check": "Invalid booking customer IDs",
            "category": "Referential Integrity",
            "errors": check_foreign_keys(
                bookings,
                "customer_id",
                customers,
                "customer_id",
            ),
        },
        {
            "check": "Invalid booking destination IDs",
            "category": "Referential Integrity",
            "errors": check_foreign_keys(
                bookings,
                "destination_id",
                destinations,
                "destination_id",
            ),
        },
        {
            "check": "Invalid payment booking IDs",
            "category": "Referential Integrity",
            "errors": check_foreign_keys(
                payments,
                "booking_id",
                bookings,
                "booking_id",
            ),
        },
        {
            "check": "Invalid traveler booking IDs",
            "category": "Referential Integrity",
            "errors": check_foreign_keys(
                travelers,
                "booking_id",
                bookings,
                "booking_id",
            ),
        },
        {
            "check": "Invalid booking dates",
            "category": "Business Rules",
            "errors": check_invalid_booking_dates(bookings),
        },
        {
            "check": "Invalid booking amounts",
            "category": "Business Rules",
            "errors": check_invalid_booking_amounts(bookings),
        },
        {
            "check": "Invalid traveler counts",
            "category": "Business Rules",
            "errors": check_invalid_traveler_counts(bookings),
        },
        {
            "check": "Traveler count mismatches",
            "category": "Consistency",
            "errors": check_traveler_counts(
                bookings,
                travelers,
            ),
        },
        {
            "check": "Payment amount mismatches",
            "category": "Consistency",
            "errors": check_payment_amounts(
                bookings,
                payments,
            ),
        },
    ]

    report = pd.DataFrame(checks)

    report["status"] = report["errors"].apply(
        lambda errors: "PASS"
        if errors == 0
        else "FAIL"
    )

    return report


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run the TripPulse data quality engine."""

    data = load_data()
    report = run_quality_checks(data)

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = REPORTS_DIR / "data_quality_report.csv"

    report.to_csv(
        report_path,
        index=False,
    )

    print("\n" + "=" * 70)
    print("TRIPPULSE DATA QUALITY REPORT")
    print("=" * 70)

    print(
        report[
            ["category", "check", "errors", "status"]
        ].to_string(index=False)
    )

    total_errors = report["errors"].sum()

    failed_checks = (
        report["status"] == "FAIL"
    ).sum()

    passed_checks = (
        report["status"] == "PASS"
    ).sum()

    print("\n" + "-" * 70)
    print(f"Checks passed: {passed_checks}")
    print(f"Checks failed: {failed_checks}")
    print(f"Total issues detected: {total_errors}")
    print(f"Report saved to: {report_path}")

    if total_errors == 0:
        print("Overall status: PASS")
    else:
        print("Overall status: FAIL")

    print("=" * 70)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()