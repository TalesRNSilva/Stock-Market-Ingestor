from dotenv import load_dotenv
import json
import datetime as dt
import os

load_dotenv()

ALPHA_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

INGETION_LOGFILE_PATH = "data/logs/ingestion.csv"

with open("data\logs\lastUpdated.json", mode = "r") as file:
    LAST_UPDATED = json.load(file)