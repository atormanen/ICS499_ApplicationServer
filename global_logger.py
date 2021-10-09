import logging
import logging.handlers
import os

VERBOSE = 15
verbose_level = 'VERBOSE'
log_file = './logs/app_server.log'

log_formatter = logging.Formatter("%(levelname)-7.7s %(process)-12.12d %(processName)-12.12s %(threadName)-12.12s %(asctime)s: %(message)s")
logger = logging.getLogger()
logging.addLevelName(VERBOSE, verbose_level)

# file_handler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
file_handler = logging.handlers.WatchedFileHandler(os.environ.get('LOGFILE', log_file))
file_handler.setFormatter(log_formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

#logger.setLevel(logging.INFO)
#logger.setLevel(verbose_level)
logger.setLevel(logging.DEBUG)


# logPath = '/var/jar_logon_server/ICS499_LogonServer/logs'
# fileName = 'logon_server.log'
