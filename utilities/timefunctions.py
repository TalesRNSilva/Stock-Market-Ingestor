import datetime

def getCurrentTimeString(type = "file"):
    currentTime = datetime.datetime.now()
    if type == "log":
        return currentTime.strftime("%Y/%m/%d-%H:%M:%S")
    elif type == "file":
        return currentTime.strftime("%Y-%m-%d - %H.%M.%S")
    else:
        print(f"Unknown type: {type}.")
        return ""