import logging

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
log_format = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%dT%H:%M:%S")
handler.setFormatter(log_format)
logger.addHandler(handler)

logger.setLevel(logging.WARNING)
