# from dotenv import load_dotenv
from dotenv import load_dotenv
import os

load_dotenv()

STOCK_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
