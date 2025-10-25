"""Tests for logging setup idempotence."""

from kryptos.log_setup import setup_logging


def test_setup_logging_idempotent():
    logger = setup_logging(level="INFO", logger_name="kryptos.test")
    before = len(logger.handlers)
    logger2 = setup_logging(level="DEBUG", logger_name="kryptos.test")
    after = len(logger2.handlers)
    assert before == after  # no duplicate handlers
    assert logger is logger2
    assert logger.level == logger2.level
