@echo off
REM ===== Clean Python/PyTest caches safely =====
cd /d "%~dp0\.."

echo [1/4] Remove __pycache__ folders...
for /f "delims=" %%D in ('dir /ad /b /s __pycache__ 2^>nul') do (
  echo   - rmdir /s /q "%%D"
  rmdir /s /q "%%D"
)

echo [2/4] Remove *.pyc files...
for /f "delims=" %%F in ('dir /a-d /b /s *.pyc 2^>nul') do (
  echo   - del /f /q "%%F"
  del /f /q "%%F"
)

echo [3/4] Remove pytest caches...
if exist ".pytest_cache" (
  echo   - rmdir /s /q ".pytest_cache"
  rmdir /s /q ".pytest_cache"
)

echo [4/4] Remove coverage artifacts...
if exist ".coverage" del /f /q ".coverage"
if exist "htmlcov" rmdir /s /q "htmlcov"

echo Done.
exit /b 0
