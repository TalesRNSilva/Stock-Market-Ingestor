import requests, os,sys
import config
from utilities.timefunctions import getCurrentTimeString
from logging_utilities import ingestionLogWrite


# This will run a single script to get historical data from 5 companies.
# File nomenclature - date and time of request / option name / compact or full data
def fetchDailyAdvantageToFile(stockOption = "TSLA", filepath = "data/raw/",outputSize = "compact"):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stockOption}&outputsize={outputSize}&apikey={config.ALPHA_API_KEY}"
    r = requests.get(url)

    if r.status_code == 200:
        filepath = f"{filepath}AV - {getCurrentTimeString()} - {stockOption} - {outputSize}.json"
        try:
            with open(file = filepath, mode='w') as file:
                file.write(r.text)
            if outputSize == "compact":
                rows = 100
            ingestionLogWrite(source = "DailyAdvantage",status = "success", rows = rows, description = f"Written Daily Records of {stockOption} to {filepath}.")
        except Exception as error:
            print(f"Error occurred: {error}.")
            ingestionLogWrite(source = "DailyAdvantage",status = "fail", rows = 0, description = f"Error: {error}.")
        
    return 






