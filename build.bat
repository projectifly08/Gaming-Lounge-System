@echo off
echo Installing Gaming Lounge Management System...

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Initialize database
echo Initializing database...
python -m src.database.init_db
if %ERRORLEVEL% NEQ 0 (
    :: Set up environment variables
    echo IMPORTANT: You need to set the correct MySQL credentials in the .env file.
    echo Please edit the .env file with your database connection details.
    echo.
    echo Press any key to open the .env file for editing...
    pause > nul
    notepad .env
    echo.
    echo After editing the .env file, press any key to continue with database initialization...
    pause > nul

    :: Initialize database again
    python -m src.database.init_db
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Database initialization failed. Please check your MySQL credentials in the .env file.
        echo Make sure your MySQL server is running and the credentials are correct.
        echo.
        pause
        exit /b 1
    )
)

python -m update_database
