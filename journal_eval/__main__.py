import argparse

from journal_eval.run import run


def main():
    parser = argparse.ArgumentParser(description="Journal Evaluation CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run evaluation over journals")
    run_parser.add_argument("--data", required=True, help="Path to data directory")
    run_parser.add_argument("--out", required=True, help="Path to output directory")

    # Default to run if no subcommand is provided (backward compatible)
    args, unknown = parser.parse_known_args()
    if args.command is None:
        # Interpret as: python -m journal_eval --data ... --out ...
        # Fall back to parsing top-level args directly
        parser = argparse.ArgumentParser(description="Journal Evaluation CLI")
        parser.add_argument("--data", required=True, help="Path to data directory")
        parser.add_argument("--out", required=True, help="Path to output directory")
        args = parser.parse_args()
        run(args.data, args.out)
        return

    if args.command == "run":
        run(args.data, args.out)


if __name__ == "__main__":
    main()
