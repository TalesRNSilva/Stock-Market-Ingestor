import requests, csv, json, datetime, os,sys
import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# This will run a single script to get historical data from 5 companies.
# File nomenclature - date and time of request / option name / compact or full data
def fetchIntradayAdvantage(stockOption = "TSLA", filepath = "data/raw",outputSize = "compact"):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stockOption}&outputsize={outputSize}&apikey={config.ALPHA_API_KEY}"
    r = requests.get(url)

    if r.status_code == 200:
        filepath = f"{filepath}/AV - {getCurrentTimeString()} - {stockOption} - {outputSize}.json"
        with open(file = filepath, mode='w') as file:
            file.write(r.text)
    
    return 

def getCurrentTimeString():
    currentTime = datetime.datetime.now()
    return currentTime.strftime("%Y-%m-%d - %H.%M.%S")





