import logging

def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
