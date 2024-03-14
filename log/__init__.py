import logging

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
log_format = logging.Formatter(fmt="%(name)s:%(levelname)s:%(message)s")
handler.setFormatter(log_format)
logger.addHandler(handler)

logger.setLevel(logging.WARNING)
