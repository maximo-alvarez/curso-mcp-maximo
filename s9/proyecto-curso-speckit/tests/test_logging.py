import logging
from app.logging_config import configurar_logging, FORMATO


def test_logging_format():
    assert "%(asctime)s" in FORMATO
    assert "%(levelname)-8s" in FORMATO
    configurar_logging("DEBUG")
    logger = logging.getLogger("test_logger")
    assert logger.isEnabledFor(logging.DEBUG)

    configurar_logging("WARNING")
    assert not logger.isEnabledFor(logging.DEBUG)
    assert logger.isEnabledFor(logging.WARNING)
