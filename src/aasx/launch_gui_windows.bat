@echo off
echo Setting up AASX Package Explorer GUI on Windows...

REM Check if VcXsrv is installed
if not exist "C:\Program Files\VcXsrv\vcxsrv.exe" (
    echo VcXsrv is not installed. Please install VcXsrv for X11 forwarding.
    echo Download from: https://sourceforge.net/projects/vcxsrv/
    echo After installation, run this script again.
    pause
    exit /b 1
)

REM Start VcXsrv if not running
tasklist /FI "IMAGENAME eq vcxsrv.exe" 2>NUL | find /I /N "vcxsrv.exe">NUL
if "%errorlevel%"=="1" (
    echo Starting VcXsrv X11 server...
    start "" "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
    timeout /t 3 /nobreak >nul
)

echo X11 server is running!
echo.
echo Now run the deployment script:
echo ./scripts/deploy-aasx-digital.sh
echo.
echo Then access the website and click "Launch AASX Package Explorer"
echo The GUI should appear in a VcXsrv window.
pause 