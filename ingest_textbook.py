from src.ingestion.pipeline import run_pipeline


def main():
    run_pipeline("data/ai_engineering_rag.pdf")


if __name__ == "__main__":
    main()
