#!/bin/bash

echo "Setting up AASX Package Explorer GUI on Windows..."

# Check if VcXsrv is installed
if [ ! -f "C:/Program Files/VcXsrv/vcxsrv.exe" ]; then
    echo "VcXsrv is not installed. Please install VcXsrv for X11 forwarding."
    echo "Download from: https://sourceforge.net/projects/vcxsrv/"
    echo "After installation, run this script again."
    read -p "Press Enter to continue..."
    exit 1
fi

# Start VcXsrv if not running
if ! tasklist //FI "IMAGENAME eq vcxsrv.exe" 2>/dev/null | grep -q "vcxsrv.exe"; then
    echo "Starting VcXsrv X11 server..."
    start "" "C:/Program Files/VcXsrv/vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
    sleep 3
fi

echo "X11 server is running!"
echo ""
echo "Now run the deployment script:"
echo "./scripts/deploy-aasx-digital.sh"
echo ""
echo "Then access the website and click 'Launch AASX Package Explorer'"
echo "The GUI should appear in a VcXsrv window."
read -p "Press Enter to continue..." 