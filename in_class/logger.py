import logging
import json
import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = ({
            "timestamp": datetime.datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        })

        for key, value in record.__dict__.items():
            if key.startswith("extra_"):
                log_entry[key.replace("extra_", "")] = value

        return json.dumps(log_entry)

#create a logger instance
logger = logging.getLogger("library")

#define default log level
logger.setLevel(logging.INFO)

# create a file handler
file_handler = logging.FileHandler("logs/library.log")
file_handler.setFormatter(JSONFormatter())

# add the file handler to the logger
logger.addHandler(file_handler)




def info(message, **kwargs):
    logger.info(message, extra=kwargs)

def error(message, **kwargs):
    logger.error(message, extra=kwargs)

def warning(message, **kwargs):
    logger.warning(message, extra=kwargs)

def debug(message, **kwargs):
    logger.debug(message, extra=kwargs)




