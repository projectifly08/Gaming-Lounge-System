@echo off
echo Installing Gaming Lounge Management System...

:: Create virtual environment
@REM echo Creating virtual environment...
@REM python -m venv venv

@REM :: Activate virtual environment
@REM echo Activating virtual environment...
@REM call venv\Scripts\activate.bat

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Set up environment variables
echo Setting up environment variables...
copy .env.example .env
echo Please edit the .env file with your database connection details.
echo IMPORTANT: You need to set the correct MySQL credentials in the .env file.
echo Current error: Access denied for user 'root'@'localhost'
echo.
echo Press any key to open the .env file for editing...
pause > nul
notepad .env
echo.
echo After editing the .env file, press any key to continue with database initialization...
pause > nul

:: Initialize database
echo Initializing database...
python -m src.database.init_db
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Database initialization failed. Please check your MySQL credentials in the .env file.
    echo Make sure your MySQL server is running and the credentials are correct.
    echo.
    pause
    exit /b 1
)

echo Installation complete!
echo To start the admin panel, run: run_admin.bat
echo To start the game launcher, run: run_launcher.bat
pause 