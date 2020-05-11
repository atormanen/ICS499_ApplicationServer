
class Manifest:

    def __init__(self):
        #Port number that the server will serve requests from
        self.port_number = 12345

        #Buffer size for the socket listening on port number above
        self.listener_buffer_size = 1024

        #Username to connect to the database
        self.database_username = 'admin'
        #Password used to connect to the database
        self.database_password = 'ICS4992020'
        #Name of the game database to connect too
        self.game_database_name = 'gamedb'
        #Name of the user database to connect too
        self.game_database_name = 'userdb'
        #Name of the reader endpoint
        self.database_reader = 'chessgamedb.cxwhpucd0m6k.us-east-2.rds.amazonaws.com'
        #name of the writer endpoint
        self.database_writer = 'chessgamedb.cxwhpucd0m6k.us-east-2.rds.amazonaws.com'

        #Set the number of request processor processes that will be available
        #to work requests as they come in.
        #!!!!!!!!!!! NOTE - System is unstable with more than 1 process running !!!!!!!!!!!
        self.number_of_request_processors = 1
        #self.number_of_request_processors = os.cpu_count()
