from dataclasses import dataclass
import datetime as dt

@dataclass
class StockDailyInfo:
    "Classe que vai mapear entradas no database de informações diárias de opções de ações."
    date: dt.date
    name: str       # Nome da ação. E.g. TSLA
    close: float   # Preço da ação no fechamento.
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
    def getFromDailyAdvantageDict(date: str, info: dict, stockName = str):
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
    def returnNullObject():
        return StockDailyInfo(date = dt.datetime.now().date(),
                              low = 0, high = 0, close = 0, volume = 0,
                              name = "ERROR")
    
    def toStr(self):
        return f"{self.date.strftime("%d/%m/%Y")} - {self.name} - {self.close}."
