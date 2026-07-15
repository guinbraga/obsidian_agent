import argparse
import sys

from run_react_agent import run_agent
from src.ingestion.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Obsidian Agent CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    ask_parser = subparsers.add_parser("ask", help="Ask the agent a question")
    ask_parser.add_argument("query", type=str, help="The prompt to send to the agent")

    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest a file source into the database"
    )
    ingest_parser.add_argument(
        "filepath", type=str, help="Path to the PDF or Markdown document"
    )

    args = parser.parse_args()

    if args.command == "ask":
        run_agent(args.query)
    elif args.command == "ingest":
        print(f"Starting ingestion for: {args.filepath}")
        run_pipeline(args.filepath)
        print("Ingestion Complete!")


if __name__ == "__main__":
    main()
