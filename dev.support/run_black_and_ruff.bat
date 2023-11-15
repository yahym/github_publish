pip install -U black ruff build && ^
cd .. && ^
ruff check --fix ./github_publish/ && ^
ruff check --fix ./setup.py && ^
black --config pyproject.toml . && ^
rem black --config pyproject.toml github_publish.spec && ^
black --config pyproject.toml setup.py

cd dev.support