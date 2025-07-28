import requests, os,sys
import config
import datetime as dt
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
                            description = f"Error while fetching and writting to file: {error}.")
        
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

def parseDailyAdvantageDict(responseDictionary, filterDate = False, dateToFilter = "1/1/1900"):
    "Essa função vai receber um dicionário de resposta da requisição e retornar uma lista de objetos StockDailyInfo"
    
    entriesList = []
    
    try:
        # O dicionário de resposta tem uma parte de metadados e
        # uma parte contendo os dados temporais. Dos metadados
        # estou apenas pegando o nome da ação. A variável entries
        # vai guardar apenas os dados do corpo da requisição.
        entries = responseDictionary["Time Series (Daily)"]
        name = responseDictionary["Meta Data"]["2. Symbol"]

        # Gerando um objeto do tipo dt.date() apenas se deseja
        # filtrar as datas de entrada. Datas menores ou iguais à
        # apontada em dateToFilter serão descartadas.
        if filterDate:
            dateFilter = dt.datetime.strptime(dateToFilter,"%d/%m/%Y").date()

        # Iterando sobre as respostas.
        for entry in entries:
            # Se a data da entrada for menor ou igual à data apontada, 
            # o objeto não é gerado e o loop apenas avança para a próxima entrada.
            if dt.datetime.strptime(entry,"%Y-%m-%d").date() <= dateFilter:
                continue
            
            # Gerando objeto do tipo StockDailyInfo para cada entrada da resposta.
            newEntry = StockDailyInfo.getFromDailyAdvantageDict(stockName = name, date = entry, info = entries[entry])
            
            # Apenas checando se o objeto foi construído corretamente.
            if newEntry.name == name:
                entriesList.append(newEntry)
            
        print(f"Generated {len(entriesList)} StockDailyInfo objects from {name}.")

    except Exception as error:
        print(f"Error while parsing response dict: {error}.")

    return entriesList