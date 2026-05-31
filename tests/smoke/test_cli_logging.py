from __future__ import annotations

import importlib
import logging
import pathlib
import tempfile
from io import StringIO
from unittest.mock import patch

cli_main_module = importlib.import_module('kryptos.cli.main')


def _run_cli(argv: list[str]):
    # Run the CLI main entrypoint with provided args
    return cli_main_module.main(argv)


def test_cli_logging_level_application():
    # Capture logs via a temporary handler
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('kryptos.cli')
    prev_handlers = list(logger.handlers)
    try:
        logger.handlers.clear()
        logger.addHandler(handler)
        exit_code = _run_cli(['--log-level', 'DEBUG', 'sections'])
        assert exit_code == 0
        handler.flush()
        contents = stream.getvalue()
        assert 'K1' in contents or 'K2' in contents or 'K3' in contents or 'K4' in contents
    finally:
        logger.handlers.clear()
        logger.handlers.extend(prev_handlers)


def test_cli_logging_quiet_flag():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('kryptos.cli')
    prev_handlers = list(logger.handlers)
    try:
        logger.handlers.clear()
        logger.addHandler(handler)
        _run_cli(['--quiet', 'sections'])
        handler.flush()
        assert stream.getvalue() == ''
    finally:
        logger.handlers.clear()
        logger.handlers.extend(prev_handlers)


def test_cli_logging_no_duplicate_handlers():
    logger = logging.getLogger('kryptos.cli')
    _run_cli(['sections'])
    mid = len([h for h in logger.handlers if getattr(h, '_kryptos_handler', False)])
    _run_cli(['sections'])
    after = len([h for h in logger.handlers if getattr(h, '_kryptos_handler', False)])
    assert mid == after  # stable across repeated invocations


def test_cli_decrypt_emits_json_and_logs():
    tmp = tempfile.NamedTemporaryFile('w+', delete=False, encoding='utf-8')
    tmp.write('ABCDEF')
    tmp.flush()
    path = pathlib.Path(tmp.name)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('kryptos.cli')
    prev_handlers = list(logger.handlers)
    try:
        logger.handlers.clear()
        logger.addHandler(handler)
        with patch('builtins.print') as mock_print:
            _run_cli(['k4-decrypt', '--cipher', str(path), '--limit', '1'])
            # JSON print should be invoked once
            json_calls = [c for c in mock_print.call_args_list if c.args and c.args[0].startswith('{')]
            assert json_calls, 'Expected JSON output'
        handler.flush()
        assert 'k4-decrypt score=' in stream.getvalue()
    finally:
        logger.handlers.clear()
        logger.handlers.extend(prev_handlers)
