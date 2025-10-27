import logging


def setup_logging(log_level):
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))