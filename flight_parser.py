
import argparse
import json
import logging
import os
import sys
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "241ADB116"
FIRST_NAME = "SanjanaGrace"
LAST_NAME = "Palla"


def create_parser():
    parser = argparse.ArgumentParser(
        description="Flight CSV parser and query tool."
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="Input CSV file")
    source.add_argument("-d", metavar="DIRECTORY", help="Input CSV directory")
    source.add_argument("-j", metavar="FILE", help="Input JSON database")

    parser.add_argument("-a", metavar="FILE", help="Airport list file")
    parser.add_argument("-o", metavar="FILE", help="Output JSON database")
    parser.add_argument("-q", metavar="FILE", help="Query JSON file")
    parser.add_argument(
        "-r",
        metavar="DIRECTORY",
        default=".",
        help="Directory for query response files"
    )

    return parser


def write_database(records, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


def write_response(results, directory):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    filename = (
        f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
    )

    output_path = os.path.join(directory, filename)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    if (args.i or args.d) and not args.a:
        parser.error("-a is required when using -i or -d")

    if args.j and args.o:
        parser.error("-o cannot be used with -j")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = None

    try:
        if args.i or args.d:
            if args.d:
                if not os.path.isdir(args.d):
                    raise FileNotFoundError(
                        f"Input directory does not exist: {args.d}"
                    )

                csv_files = sorted(
                    os.path.join(args.d, name)
                    for name in os.listdir(args.d)
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                )

                if not csv_files:
                    raise ValueError(
                        f"No CSV files found in directory: {args.d}"
                    )

            else:
                if not os.path.isfile(args.i):
                    raise FileNotFoundError(
                        f"Input CSV file does not exist: {args.i}"
                    )

                csv_files = [args.i]

            if not os.path.isfile(args.a):
                raise FileNotFoundError(
                    f"Airport file does not exist: {args.a}"
                )

            airports = load_airports(args.a)
            records, errors = parse_files(csv_files, airports)

            output_path = args.o if args.o else "db.json"

            output_directory = os.path.dirname(
                os.path.abspath(output_path)
            )

            if not os.path.isdir(output_directory):
                raise FileNotFoundError(
                    f"Output directory does not exist: {output_directory}"
                )

            log_path = os.path.join(output_directory, "errors.log")

            handler = logging.FileHandler(
                log_path,
                mode="w",
                encoding="utf-8"
            )

            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )

            logger.addHandler(handler)

            for error in errors:
                logger.warning(error)

            write_database(records, output_path)

            print(f"Valid flights: {len(records)}")
            print(f"Invalid rows: {len(errors)}")
            print(f"Database saved: {output_path}")
            print(f"Error log saved: {log_path}")

            database = records

        else:
            if not os.path.isfile(args.j):
                raise FileNotFoundError(
                    f"JSON database does not exist: {args.j}"
                )

            with open(args.j, "r", encoding="utf-8") as file:
                database = json.load(file)

            if not isinstance(database, list) or not all(
                isinstance(record, dict) for record in database
            ):
                raise ValueError(
                    "JSON database must contain an array of objects."
                )

        if args.q:
            if not os.path.isfile(args.q):
                raise FileNotFoundError(
                    f"Query file does not exist: {args.q}"
                )

            if not os.path.isdir(args.r):
                raise FileNotFoundError(
                    f"Response directory does not exist: {args.r}"
                )

            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if isinstance(queries, dict):
                pass
            elif isinstance(queries, list) and all(
                isinstance(query, dict) for query in queries
            ):
                pass
            else:
                raise ValueError(
                    "Query file must contain an object or an array of objects."
                )

            results = run_queries(database, queries)
            response_path = write_response(results, args.r)

            print(f"Query response saved: {response_path}")

        return 0

    except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
