from fetchData import initializeAllStocks, updateStocks, updateStock, testConnection
from datamodels import PGController
from config import DB_CREDENTIALS, ACTIVE_STOCKS

# Run this exactly once. Only do this after you've set up .env variables. Otherwise it will fail.
def initializeDatabase(credentials = DB_CREDENTIALS,
                       create_tables = True,
                       truncate = True):
    "Essa função vai criar as tabelas apropriadas no database e inserir os dados, se necessário."

    if not testConnection(credentials=credentials):
        print("Connection failed to DB.")
        return
    else:
        controller = PGController(database_name=credentials['name'],
                                  user = credentials['user'],
                                  password = credentials['password'])

    # Garantindo que o usuário não está fazendo besteira.    
    response = input(f"Initializing your DB. This will likely fetch a huge amount of data and delete all current info on your Database.\nAre you sure? (y/n) ")
    if response not in "yY":
        return

    if create_tables:
        controller.createStockTables()
        # Todo: inserir descrições das ações no DB.

    initializeAllStocks(controller = controller, truncate = truncate)

def scheduledUpdate(credentials = DB_CREDENTIALS):
    if not testConnection(credentials=credentials):
        print("Connection to DB failed.")
        return
    else:
        print("Connection to DB Stablished.")
        controller = PGController(database_name=credentials['name'],
                                  user = credentials['user'],
                                  password = credentials['password'])
        
    print(f"Updating all stock in the list {ACTIVE_STOCKS}...")
    updateStocks(controller = controller)
    print("Update finished.")

def main():
    # Execute the function intializeDatabase() exactly ONE TIME
    scheduledUpdate()

main()