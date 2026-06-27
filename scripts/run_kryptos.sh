#!/bin/bash
PORT=$(python3 scripts/find_free_port.py)
echo "Starting Kryptos on port $PORT"
docker run -d -p $PORT:8000 -v .:/app kryptos-dev python -m kryptos.cli.main serve --port $PORT
