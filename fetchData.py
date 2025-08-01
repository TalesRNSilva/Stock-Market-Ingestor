import requests, os,sys
import config
import datetime as dt
from utilities.timefunctions import getCurrentTimeString
from logging_utilities import ingestionLogWrite, updateLastFetchDate
from datamodels import StockDailyInfo, PGController

# This will run a single script to get historical data from a company and store into a file.
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
    # Lembrando que esse dicionário está dividido em metadados e corpo da requisição."

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

def parseDailyAdvantageDict(responseDictionary, filterDate = False, dateToFilter = dt.date(1900,1,1)):
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
            dateFilter = dateToFilter

        # Iterando sobre as respostas.
        for entry in entries:
            # Se a data da entrada for menor ou igual à data apontada, 
            # o objeto não é gerado e o loop apenas avança para a próxima entrada.
            if filterDate:
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

def initializeAllStocks(controller: PGController,
                        stockList = config.ACTIVE_STOCKS,
                        truncate = False,
                        filterDate = False,
                        outputSize = 'full'):
        "Popula o DB com os dados das ações definidas no arquivo config.py."
        # Se a opção truncate for True, deleta dos os dados da tabela.
        if truncate: 
            controller.clearAllStockData()
        
        for stock in stockList:
            dictResponse = fetchDailyAdvantageToJSON(stockOption=stock, outputSize=outputSize)
            if filterDate:
                dateToFilter = controller.getLastUpdateDate(stock_name=stock)
            else:
                dateToFilter = dt.date(1900,1,1)
            entryList = parseDailyAdvantageDict(dictResponse, filterDate = filterDate, dateToFilter=dateToFilter)
            controller.insertStockInfoBulk(entryList)
            lastDate = controller.getLastUpdateDate(stock).strftime('%Y-%m-%d')
            updateLastFetchDate(stockName=stock, date=lastDate)

def initializeStock(controller: PGController,
                        stockname = 'TSLA',
                        delete = False,
                        filterDate = False,
                        outputSize = 'full'):
    "Essa função popula o DB com os valores de uma ação específica."
    # Se parâmetro estiver marcado, remove os valores correspondentes àquela ação.
    if delete:
        controller.query(f"Delete from {controller.stock_data_table} where stock_name = {stockname}.")
     
    dictResponse = fetchDailyAdvantageToJSON(stockOption=stockname, outputSize=outputSize)
    
    if filterDate:
        dateToFilter = controller.getLastUpdateDate(stock_name=stockname)
    else:
        dateToFilter = dt.date(1900,1,1)

    entryList = parseDailyAdvantageDict(dictResponse, filterDate = filterDate, dateToFilter=dateToFilter)
    controller.insertStockInfoBulk(entryList)
    lastDate = controller.getLastUpdateDate(stockname).strftime('%Y-%m-%d')
    updateLastFetchDate(stockName=stockname, date=lastDate)

def updateStock(controller: PGController,
                        stockname = 'TSLA',
                        outputSize = 'compact'):
    "Atualiza certa ação no DB, inserindo apenas dados posteriores à última inserção."
    # Fazendo a requisição à API.
    dictResponse = fetchDailyAdvantageToJSON(stockOption=stockname, outputSize=outputSize)

    # Determinando qual a data da última atualização da ação.
    dateToFilter = controller.getLastUpdateDate(stock_name=stockname)

    # Filtrando o dicionário obtido como resposta com base na data,
    # e parsando as entradas em objetos do tipo StockDailyInfo.
    entryList = parseDailyAdvantageDict(dictResponse, filterDate = True, dateToFilter=dateToFilter)

    # Pedindo ao controlador para inserir as entradas resultantes no DB.
    controller.insertStockInfoBulk(entryList)
    
    # Atualizando data da última atualização no arquivo JSON adequado.
    lastDate = controller.getLastUpdateDate(stockname).strftime('%Y-%m-%d')
    updateLastFetchDate(stockName=stockname, date=lastDate)

def testConnection(credentials = config.DB_CREDENTIALS) -> bool:
    "Verificador básico de conexão."
    try:
        connection = PGController(database_name=credentials['name'],
                                  user = credentials['user'],
                                  password = credentials['password'])
        return True
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def updateStocks(controller:PGController,
                 stockList:list = config.ACTIVE_STOCKS,
                 outputSize:str = 'compact'):
    "Atualiza todos as ações em uma lista."
    
    for stock in stockList:
        updateStock(controller=controller,
                    stockname=stock,
                    outputSize=outputSize)

