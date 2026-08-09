uv run black -l 110 src main.py run.py index-meta-proxy
uv run ruff check --fix src main.py run.py index-meta-proxy
uv run mypy src main.py run.py index-meta-proxy