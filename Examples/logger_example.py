import logging
logging.basicConfig(filename="logs/example.log", format="%(levelname)s\t| %(asctime)s\t| %(message)s", encoding="utf-8", level=logging.DEBUG)
logging.debug("This message should go to the log file")
logging.info("So should this")
logging.warning("And this too!")
logging.error("this is just an error - for funsies!")