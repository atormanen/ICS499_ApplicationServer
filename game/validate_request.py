# Validate request will check the initial variable to see what kind of request
# type it is.
## TODO: Check the entire json object for apropriate fields and not just the req type
class ValidateRequest:

    def __init__(self):
        self.num = 0

    def isBadRequest(self, parsedData):
        try:
            if parsedData["request_type"] == "MakeMove":
                return False
            elif parsedData["request_type"] == "CreateGame":
                return False
            elif parsedData["request_type"] == "AcceptGame":
                return False
            elif parsedData["request_type"] == "CheckForGame":
                return False
            elif parsedData["request_type"] == "RequestGame":
                return False
            elif parsedData["request_type"] == "RequestGameCanceled":
                return False
            else:
                return True
        except KeyError:
            print("KeyError")
