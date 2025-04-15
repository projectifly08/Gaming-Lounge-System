@echo off

REM Call the install.bat script first
call build.bat

echo Building Gaming Lounge System executables...

REM Find Python executable
FOR /F "tokens=*" %%g IN ('where python') do (SET PYTHON_PATH=%%g)
echo Python found at: %PYTHON_PATH%

REM Install PyInstaller using the Python module approach
echo Installing PyInstaller...
"%PYTHON_PATH%" -m pip install pyinstaller

REM Build the Launcher executable directly
echo.
echo Building Launcher executable...
"%PYTHON_PATH%" -m PyInstaller --onefile ^
  --name=Launcher ^
  --icon="src/assets/logo1.jpg" ^
  --add-data "src/assets;src/assets" ^
  --add-data "src/database/*.sql;src/database" ^
  --hidden-import=PyQt5.QtCore ^
  --hidden-import=PyQt5.QtGui ^
  --hidden-import=PyQt5.QtWidgets ^
  --hidden-import=mysql.connector ^
  --hidden-import=bcrypt ^
  --hidden-import=python-dotenv ^
  run_launcher.py

REM Build the Admin executable directly
echo.
echo Building Admin executable...
"%PYTHON_PATH%" -m PyInstaller --onefile ^
  --name=Admin ^
  --icon="src/assets/logo1.jpg" ^
  --add-data "src/assets;src/assets" ^
  --add-data "src/database/*.sql;src/database" ^
  --hidden-import=PyQt5.QtCore ^
  --hidden-import=PyQt5.QtGui ^
  --hidden-import=PyQt5.QtWidgets ^
  --hidden-import=mysql.connector ^
  --hidden-import=bcrypt ^
  --hidden-import=python-dotenv ^
  run_admin.py

echo.
if exist "dist\Launcher.exe" (
    echo Launcher build completed successfully!
) else (
    echo Launcher build failed!
)

if exist "dist\Admin.exe" (
    echo Admin build completed successfully!
) else (
    echo Admin build failed!
)

echo.
echo Installation complete!
echo.
echo Check the 'dist' directory for the executables.
echo To start the admin panel, run: Admin.exe
echo To start the game launcher, run: Launcher.exe
echo.
pause 
