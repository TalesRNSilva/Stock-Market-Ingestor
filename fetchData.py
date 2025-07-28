import requests, os,sys
import config
from utilities.timefunctions import getCurrentTimeString
from logging_utilities import ingestionLogWrite
from datamodels import StockDailyInfo

# This will run a single script to get historical data from 5 companies.
# File nomenclature - date and time of request _ option name _ output Size
def fetchDailyAdvantageToFile(stockOption = "TSLA", filepath = "data/raw/",outputSize = "compact"):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stockOption}&outputsize={outputSize}&apikey={config.ALPHA_API_KEY}"
    
    try:
        # Garantindo que o caminho existe e abrindo de modo seguro.
        os.makedirs(filepath, exist_ok=True)
        filename = f"AV_{getCurrentTimeString()}_{stockOption}_{outputSize}.json"
        full_path = os.path.join(filepath, filename)

        r = requests.get(url)
        r.raise_for_status()

        # Escrevendo o conteúdo no arquivo.
        with open(file = full_path, mode='w') as file:
            file.write(r.text)

        # Estimando o número de colunas.
        rows = 100 if outputSize == "compact" else 500
        
        # Logando o resultado.
        ingestionLogWrite(source = "DailyAdvantage",
                        status = "success",
                        rows = rows,
                        description = f"Written Daily Records of {stockOption} to {filepath}.")

    except Exception as error:
        # Imprimindo e logando o erro.   
        print(f"Error occurred: {error}.")
        ingestionLogWrite(source = "DailyAdvantage",
                            status = "fail",
                            rows = 0,
                            description = f"Error: {error}.")
        
    return 

def fetchDailyAdvantageToJSON(stockOption = "TSLA", outputSize = "compact"):
    "Essa função vai fazer um request para o site e devolver um dicionário da resposta."

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stockOption}&outputsize={outputSize}&apikey={config.ALPHA_API_KEY}"

    try:
        r = requests.get(url)
        r.raise_for_status()
        
        dictionary = r.json()
        return dictionary

    except Exception as error:
        print(f"Error while requesting: {error}")
        ingestionLogWrite(source = "DailyAdvantage",
                            status = "fail",
                            rows = 0,
                            description = f"Error while requesting: {error}.")

    return

def parseDailyAdvantageDict(responseDictionary, restrictDate = False):
    "Essa função vai receber um dicionário de resposta da requisição e retornar uma lista de objetos StockDailyInfo"
    
    entriesList = []
    
    try:
        entries = responseDictionary["Time Series (Daily)"]
        name = responseDictionary["Meta Data"]["2. Symbol"]
        for entry in entries:

            newEntry = StockDailyInfo.getFromDailyAdvantageDict(stockName = name, date = entry, info = entries[entry])
           
            if not newEntry.name == "ERROR":
                entriesList.append(newEntry)

    except Exception as error:
        print(f"Error while parsing dict: {error}.")

    return entriesList