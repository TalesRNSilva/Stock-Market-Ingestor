import csv, os, json
from utilities.timefunctions import getCurrentTimeString

def ingestionLogWrite(source = "unknown", filepath = "data/logs/ingestion.csv", status = "success", rows = 0, description = "none"):
    
    # Estrutura do CSV para logar ingestão de dados:
    # date / source / status / rows / description
    date = getCurrentTimeString("log")

    try:
        with open(filepath, mode = "a", newline = "") as file:
            writer = csv.writer(file)
            writer.writerow([date,source,status,rows,description])
        print(f"Logfile {filepath} updated.")
        print(f"Log: {date} | {source} | {status} | {rows} | {description}")
        return
    except Exception as error:
        print(f"Something unexpected happened. Error: {error}.")
        return

def updateLastFetchDate(stockName: str, date: str, filepath="data/logs/lastUpdated.json"):
    "Atualiza a última data de atualização no arquivo JSON definido."
    # Lembrando: date está formatado como "%d/%m/%Y"
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[stockName] = date

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Error updating last fetch date: {e}")
    
