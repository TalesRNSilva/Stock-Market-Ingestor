from dotenv import load_dotenv
import json
import datetime as dt
import os

load_dotenv()

ALPHA_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

INGETION_LOGFILE_PATH = "data/logs/ingestion.csv"

with open("data\logs\lastUpdated.json", mode = "r") as file:
    LAST_UPDATED = json.load(file)

ACTIVE_STOCKS = ["TSLA",    # Tesla    
                  "IBM",    # IBM
                  "PEP",    # Pepsi co
                  "BA",     # Boeing
                  "JNJ"]    # Johnson & Johnson

# As credenciais estão definidas no arquivo .env, oculto.
DB_CREDENTIALS = {
    'name' : os.getenv("DB_NAME"),
    'user' : os.getenv("DB_USER"),
    'password' : os.getenv("DB_PASSWORD"),
    'host' : os.getenv("DB_HOST"),
    'port' : os.getenv("DB_PORT")
}

# Nome das tabelas no meu DB
TABLES_INFO = { 
    "stock description" : 'stock_info',
    'stock historical data' : 'stock_data'
}