from dataclasses import dataclass
from config import DB_CREDENTIALS, TABLES_INFO, ACTIVE_STOCKS
from logging_utilities import ingestionLogWrite, updateLastFetchDate
import datetime as dt
import psycopg2 as pg

@dataclass
class StockDailyInfo:
    "Classe que vai mapear entradas no database de informações diárias de opções de ações."
    date: dt.date
    name: str       # Nome da ação. E.g. TSLA
    close: float    # Preço da ação no fechamento.
    high: float     # Maior valor no dia
    low: float      # Menor valor no dia   
    volume: int     # Número de ações disponíveis.

    # O modo como o JSON do VA está estruturado é como um grande dicionário
    # cuja chave é uma string de data "2025-07-25" e o valor é um dicionário contendo
    # informações como low, high, closed e volume.
    # E.g. "2025-07-25": {
    #        "1. open": "308.7400",
    #        "2. high": "323.6300",
    #        "3. low": "308.0100",
    #        "4. close": "316.0600",
    #        "5. volume": "148227027"
    #   }
    @staticmethod
    def getFromDailyAdvantageDict(date: str, info: dict, stockName: str):
        "Função que vai retornar um objeto StockDailyInfo a partir de dicionário do JSON da API do Daily Advantage."
        try: 
            date = dt.datetime.strptime(date, "%Y-%m-%d").date()
            return StockDailyInfo(date = date,
                              low = float(info["3. low"]),
                              high = float(info["2. high"]),
                              close = float(info["4. close"]),
                              volume = int(info["5. volume"]),
                              name = stockName)
        except Exception as error:
            print(f"Error while building dataclass: {error}")
            return StockDailyInfo.returnNullObject()
    
    # Retorna um objeto com entradas nulas.
    @staticmethod
    def returnNullObject():
        return StockDailyInfo(date = dt.datetime.now().date(),
                              low = 0, high = 0, close = 0, volume = 0,
                              name = "ERROR")
    
    def toStr(self):
        return f"{self.date.strftime("%Y-%m-%d")} - {self.name} - {self.close}."
    
    def __str__(self):
        return f"Stock Info Object (name, date, low, high, self, close, volume)\n('{self.name}', '{self.datestr}', {self.low}, {self.high}, {self.close}, {self.volume})"

    @property
    def datestr(self):
        return self.date.strftime("%Y-%m-%d")

    def toDict(self):
        return {
            "date" : self.date.strftime("%Y-%m-%d"),
            "name" : self.name,
            "close": self.close,
            "low"  : self.low,
            "high" : self.high,
            "volume" : self.volume
        }
    
    @staticmethod
    def fromDict(dictionary):
        try:
            stockObject = StockDailyInfo (
            date = dt.datetime.strptime(dictionary["date"]).date(),
            name = dictionary["name"],
            high = dictionary["high"],
            low =  dictionary["low"],
            close = dictionary["close"],
            volume = dictionary["volume"]
        )
        except Exception as e:
            print(f"Error while building StockObject from Dictionary: {e}")
            stockObject = StockDailyInfo.returnNullObject()
        
        return stockObject

#Controlará acesso ao meu db
class PGController:
    def __init__(self, database_name = DB_CREDENTIALS['name'], 
                 host = DB_CREDENTIALS['host'], 
                 user = DB_CREDENTIALS['user'], 
                 password = DB_CREDENTIALS['password'], 
                 port = DB_CREDENTIALS['port']):
        self.dbname = database_name
        # Criando o conector com o servidor PostGre
        # Para documentação do objeto connection - https://www.psycopg.org/docs/connection.html
        self.connector = pg.connect(dbname = database_name,
                                    user = user,
                                    password = password)
        # Colocando a conexão no modo autocommit.
        self.connector.set_session(autocommit=True)
        # É a interface que executará os comandos.
        # Documentação do objeto cursor - https://www.psycopg.org/docs/cursor.html#cursor
        self.cursor = self.connector.cursor()
    
        self.stock_info_table = 'stock_info'
        self.stock_data_table = 'stock_data'

    # Apenas para facilitar os queries.    
    def query(self, query = ""):
        self.cursor.execute(query)

    def commit(self):
        self.connector.commit()

    def fetch(self):
        return self.cursor.fetchone()
    
    def fetchall(self):
        return self.cursor.fetchall()

    # Se o modo autocommit estiver ligado, mantenha a variável commit no falso.
    def insertStockInfoObject(self, stockInfo = StockDailyInfo.returnNullObject(), commit = False):
        try:
            queryString = f"INSERT INTO public.{self.stock_data_table} (stock_name,date,low,high,close,volume) VALUES ('{stockInfo.name}', '{stockInfo.datestr}', {stockInfo.low}, {stockInfo.high}, {stockInfo.close}, {stockInfo.volume});"
            #print(queryString)
            self.query(queryString)
            if commit:
                self.commit()
            return 1
        except Exception as e:
            print(f"Value not inserted into DB. Error: {e}")
            return 0
        
    def insertStockInfoBulk(self, stockObjectList = []):
        if not stockObjectList:
            print("StockInfo object list is empty. No entries added.")
            return
        # Recuperando o nome da ação para fins de registro.
        name = stockObjectList[0].name
        # Para rastrear taxa de sucesso da transação.
        successes = 0
        total = len(stockObjectList)
        for stockInfo in stockObjectList:
            # Se o modo autocommit estiver ligado, mantenha a variável commit no falso.
            successes += self.insertStockInfoObject(stockInfo, commit = False)

        status = "success" if successes else "fail"

        print(f"Total of {successes} {name} entries out of {total} inserted into Database.")
        ingestionLogWrite(source = "AlphaVantage",
                          status = status,
                          rows = successes,
                          description = f"{successes} {name} entries added into database out of {total}. {total-successes} rows not inserted.")
        return

    # Retorna a data da última entrada de uma certa ação no DB.
    def getLastUpdateDate(self, stock_name = 'STOCK'):
        self.query(f"select max(date) from {self.stock_data_table} where stock_name = '{stock_name}' group by stock_name;")
        queryResult = self.fetch()
        if queryResult:
            print(f"Última atualização de {stock_name}: {queryResult[0].strftime("%Y-%m-%d")}")
            return queryResult[0]
        else:
            print("Ação não encontrada no DB. Retornando data coringa.")
            return dt.date(1900,1,1)
        
    def getStocklistFromDB(self):
        returnList = []
        self.query(f"select stock_name from {self.stock_info_table};")
        for item in self.fetchall():
            returnList.append(item[0])
        return returnList
    
    def updateAllUpdateDates(self, stockList = ACTIVE_STOCKS):
        "Atualiza o arquivo json que rastreia a última atualização com base na última inserção no database."
        for stock in stockList:
            stockDate = self.getLastUpdateDate(stock).strftime('%Y-%m-%d')
            updateLastFetchDate(stockName=stock, date=stockDate)

    def createStockTables(self):
        "Cria as tabelas onde os dados serão armazenados."
        print("Trying to generate tables into DB.")
        try: 
            stock_info_query =  "CREATE TABLE IF NOT EXISTS public.stock_info (sock_name varchar NOT NULL,description varchar NULL,full_name varchar NOT NULL,CONSTRAINT stock_info_pk PRIMARY KEY (stock_name));"
            stock_data_query = 'CREATE TABLE IF NOT EXISTS public.stock_data (stock_name varchar NOT NULL,"date" date NOT NULL,low float4 NULL,high float4 NULL,"close" float4 NOT NULL,volume int4 NULL,CONSTRAINT unique_date_name UNIQUE (date, stock_name));'
            fk_query = 'ALTER TABLE public.stock_data ADD CONSTRAINT stock_name FOREIGN KEY (stock_name) REFERENCES public.stock_info(stock_name);'
            self.query(stock_info_query)
            self.query(stock_data_query)
            self.query(fk_query)
            print("Tables created succefully.")
        except Exception as e:
            print(f"Not possible to create tables: {e}")

    def clearAllStockData(self):
        "Limpa os dados da tabela stock_data DB."
        print(f"This will clear all the stock data on the table {self.stock_data_table}. Are you sure? (y/n)")
        response = input()

        if response in "yY":
            self.query(f"TRUNCATE TABLE public.{self.stock_data_table};")
        else:
            print("Data not cleared.")

    def clearStockData(self, stockName = 'TSLA'):
        "Limpa os dados de determinada ação no DB."
        print(f"This will clear all the stock data from {stockName} on the table {self.stock_data_table}. Are you sure? (y/n)\n")
        
        response = input()
        if response in "yY":
            self.query(f"DELETE FROM public.{self.stock_data_table} where stock_name = {stockName};")
        else:
            print("Data not cleared.")