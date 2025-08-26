$ErrorActionPreference = 'Stop'
python manage.py check
if ($LASTEXITCODE -ne 0) { exit 1 }
python manage.py makemigrations --check
if ($LASTEXITCODE -ne 0) { exit 1 }
python manage.py migrate
if ($LASTEXITCODE -ne 0) { exit 1 }
pytest -q --create-db
if ($LASTEXITCODE -ne 0) { exit 1 }
