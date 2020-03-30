#Validate request will check the initial variable to see what kind of request
#type it is.
## TODO: Check the entire json object for apropriate fields and not just the req type
class ValidateRequest:

    def __init__(self):
        self.num = 0

    def isBadRequest(self,parsedData):
        try:
            if parsedData["requestType"] == "MakeMove":
                return False
            elif parsedData["requestType"] == "CreateGame":
                return False
            elif parsedData["requestType"] == "AcceptGame":
                return False
            elif parsedData["requestType"] == "CheckForGame":
                return False
            elif parsedData["requestType"] == "RequestGame":
                return False
            else:
                return True
        except KeyError:
            print("KeyError")
