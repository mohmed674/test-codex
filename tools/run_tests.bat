@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ===== ERP_CORE Test Runner (SCOPED to ERP_CORE/tests) =====
REM - Rebuilds test DB using pytest with config.pytest_settings
REM - Runs ONLY tests under ERP_CORE/tests to avoid external collisions
REM - Stores auto summaries in /reports (from project conftest.py)
REM ============================================================

cd /d "%~dp0\.."

set PYTHON=env\Scripts\python.exe
set TESTPATH=ERP_CORE\tests

if not exist "%PYTHON%" (
  echo [ERROR] Could not find venv Python at "%PYTHON%".
  echo Create/activate venv first:  python -m venv env
  exit /b 1
)

if not exist "%TESTPATH%" (
  echo [ERROR] Tests folder not found: %TESTPATH%
  exit /b 1
)

if not exist "reports" mkdir "reports"

echo.
echo =======================
echo [1/3] Rebuild test DB
echo =======================
"%PYTHON%" -m pytest "%TESTPATH%" --ds=config.pytest_settings --create-db
if errorlevel 1 (
  echo [ERROR] Failed while creating test DB. See output above.
  exit /b 1
)

echo.
echo ======================================
echo [2/3] Run tests with coverage reports
echo ======================================
"%PYTHON%" -m pytest "%TESTPATH%" --ds=config.pytest_settings
set EXITCODE=%ERRORLEVEL%

echo.
echo ===========================
echo [3/3] Snapshot HTML report
echo ===========================
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set TODAY=%%d%%b%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a%%b
set NOW=%NOW::=%
set SNAP=reports\coverage_%TODAY%_%NOW%.html

if exist "htmlcov\index.html" (
  copy /y "htmlcov\index.html" "%SNAP%" >nul
  echo [OK] Coverage snapshot: %SNAP%
) else (
  echo [WARN] htmlcov\index.html not found. Skipping snapshot.
)

echo.
if exist "reports\test_summary.md" (
  echo ===== Auto Test Summary (reports\test_summary.md) =====
  type "reports\test_summary.md"
  echo =======================================================
) else (
  echo [WARN] Auto summary not found (reports\test_summary.md).
)

echo.
echo Exit code: %EXITCODE%
exit /b %EXITCODE%
