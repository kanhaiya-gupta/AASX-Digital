# X11 Forwarding Setup for AASX Package Explorer GUI on Windows
Write-Host "Setting up X11 forwarding for AASX Package Explorer GUI on Windows..." -ForegroundColor Green

# Check if VcXsrv is installed
$vcxsrvPath = "C:\Program Files\VcXsrv\vcxsrv.exe"
if (-not (Test-Path $vcxsrvPath)) {
    Write-Host "VcXsrv is not installed. Please install VcXsrv for X11 forwarding." -ForegroundColor Red
    Write-Host "Download from: https://sourceforge.net/projects/vcxsrv/" -ForegroundColor Yellow
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}

# Set environment variables
$env:DISPLAY = "localhost:0.0"
$env:XAUTHORITY = "$env:USERPROFILE\.Xauthority"

# Create .Xauthority file if it doesn't exist
if (-not (Test-Path "$env:USERPROFILE\.Xauthority")) {
    Write-Host "Creating .Xauthority file..." -ForegroundColor Yellow
    New-Item -Path "$env:USERPROFILE\.Xauthority" -ItemType File -Force | Out-Null
}

# Check if VcXsrv is running
$vcxsrvProcess = Get-Process -Name "vcxsrv" -ErrorAction SilentlyContinue
if (-not $vcxsrvProcess) {
    Write-Host "Starting VcXsrv X11 server..." -ForegroundColor Yellow
    Start-Process -FilePath $vcxsrvPath -ArgumentList ":0", "-multiwindow", "-clipboard", "-wgl", "-ac" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

Write-Host "X11 forwarding setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To launch AASX Package Explorer with GUI:" -ForegroundColor Cyan
Write-Host "1. Make sure VcXsrv is running (X11 server)" -ForegroundColor White
Write-Host "2. Run: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d" -ForegroundColor White
Write-Host "3. Access the website and click 'Launch AASX Package Explorer'" -ForegroundColor White
Write-Host ""
Write-Host "The GUI should now appear in a VcXsrv window." -ForegroundColor Green
Write-Host ""
Write-Host "Environment variables set:" -ForegroundColor Cyan
Write-Host "DISPLAY: $env:DISPLAY" -ForegroundColor White
Write-Host "XAUTHORITY: $env:XAUTHORITY" -ForegroundColor White

Read-Host "Press Enter to continue" 