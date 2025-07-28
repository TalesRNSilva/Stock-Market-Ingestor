from dotenv import load_dotenv
import os

load_dotenv()

ALPHA_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

INGETION_LOGFILE_PATH = "data/logs/ingestion.csv"
