"""CSV file loading, row validation and duplicate detection."""

import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Parse CSV files and return valid records and error messages."""

    records = []
    errors = []

    # Store flight ID and departure time to detect duplicates
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8", newline="") as file:

            for line_number, line in enumerate(file, start=1):

                # Skip the first line (CSV header)
                if line_number == 1:
                    continue

                # Skip blank lines
                if not line.strip():
                    continue

                # Skip comment lines
                if line.lstrip().startswith("#"):
                    continue

                # Parse the current CSV line
                try:
                    row = next(csv.reader([line]))
                except csv.Error:
                    errors.append(
                        f"{filename}:{line_number}: WRONG_FIELD_COUNT | {line.rstrip()}"
                    )
                    continue

                # Remove whitespace from fields
                row = [field.strip() for field in row]

                # Validate the row
                error_code = validate_row(row, airports)

                if error_code is not None:
                    errors.append(
                        f"{filename}:{line_number}: {error_code} | {line.rstrip()}"
                    )
                    continue

                # Check for duplicate flights
                flight_key = (row[0], row[3])

                if flight_key in seen_flights:
                    errors.append(
                        f"{filename}:{line_number}: DUPLICATE_FLIGHT | {line.rstrip()}"
                    )
                    continue

                # Save valid flight
                seen_flights.add(flight_key)
                records.append(to_record(row))

    return records, errors
