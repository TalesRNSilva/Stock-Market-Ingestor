import csv
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


    
