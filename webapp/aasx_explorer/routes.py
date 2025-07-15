"""
AASX Package Explorer Routes
Provides routes for the AASX Package Explorer information and download pages
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
import sys

# Add the src directory to the path to import the launcher
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

# Create FastAPI Router
router = APIRouter(tags=["AASX Explorer"])

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

@router.get("/", response_class=HTMLResponse)
async def aasx_explorer_page(request: Request):
    """AASX Package Explorer main information page"""
    return templates.TemplateResponse("aasx_explorer/index.html", {"request": request})

@router.get("/download", response_class=FileResponse)
async def download_aasx_explorer():
    """Download the AASX Package Explorer executable"""
    file_path = Path("AasxPackageExplorer/AasxPackageExplorer.exe")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="AASX Package Explorer executable not found")
    
    return FileResponse(
        path=file_path,
        filename="AasxPackageExplorer.exe",
        media_type="application/octet-stream"
    )

@router.get("/download-zip", response_class=FileResponse)
async def download_aasx_explorer_zip():
    """Download the AASX Package Explorer zip file"""
    zip_path = Path("data/aasx-package-explorer.2025-03-25.alpha.zip")
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="AASX Package Explorer zip file not found")
    
    return FileResponse(
        path=zip_path,
        filename="aasx-package-explorer.2025-03-25.alpha.zip",
        media_type="application/zip"
    )

@router.post("/launch", response_class=JSONResponse)
async def launch_aasx_explorer():
    """Launch the AASX Package Explorer application"""
    try:
        import subprocess
        import platform
        
        # Check platform
        if platform.system() != "Windows":
            raise HTTPException(status_code=400, detail="AASX Package Explorer is a Windows application only")
        
        # Find the executable
        explorer_path = Path("AasxPackageExplorer/AasxPackageExplorer.exe")
        
        if not explorer_path.exists():
            raise HTTPException(status_code=404, detail="AASX Package Explorer executable not found")
        
        # Launch the application directly
        process = subprocess.Popen([str(explorer_path)])
        
        return {
            "success": True,
            "message": "AASX Package Explorer launched successfully",
            "pid": process.pid,
            "executable_path": str(explorer_path)
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching AASX Package Explorer: {str(e)}")

@router.get("/status", response_class=JSONResponse)
async def get_aasx_explorer_status():
    """Get the status of AASX Package Explorer"""
    try:
        import platform
        import psutil
        
        # Check if executable exists
        explorer_path = Path("AasxPackageExplorer/AasxPackageExplorer.exe")
        executable_found = explorer_path.exists()
        
        # Check if running
        running = False
        pid = None
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                if 'aasxpackageexplorer' in proc_name:
                    running = True
                    pid = proc_info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "success": True,
            "executable_found": executable_found,
            "executable_path": str(explorer_path) if executable_found else None,
            "running": running,
            "pid": pid,
            "platform": platform.system()
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "psutil not available for process checking"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/license", response_class=HTMLResponse)
async def license_page(request: Request):
    """License information page"""
    return templates.TemplateResponse("aasx_explorer/license.html", {"request": request})

@router.get("/guide", response_class=HTMLResponse)
async def user_guide_page(request: Request):
    """User guide and tutorial page"""
    return templates.TemplateResponse("aasx_explorer/guide.html", {"request": request}) 