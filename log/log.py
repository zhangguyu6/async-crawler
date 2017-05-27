import logging

logger = logging.getLogger("crawler")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
filehandler = logging.FileHandler("log.txt")
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%y%m%d %H:%M:%S')

handler.setFormatter(formatter)
filehandler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(filehandler)