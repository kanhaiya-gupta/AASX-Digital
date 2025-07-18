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
        # Import the launcher module
        from src.aasx.launch_explorer import launch_explorer as launch_aasx_explorer
        
        # Launch the explorer using the module
        result = launch_aasx_explorer(silent=True)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "pid": result.get("pid"),
                "executable_path": result["explorer_path"],
                "method": result.get("method", "unknown"),
                "platform": result.get("platform", "unknown")
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except ImportError as e:
        raise HTTPException(status_code=404, detail=f"AASX Package Explorer launcher module not found: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching AASX Package Explorer: {str(e)}")

@router.get("/status", response_class=JSONResponse)
async def get_aasx_explorer_status():
    """Get the status of AASX Package Explorer"""
    try:
        # Import the launcher module for status checking
        from src.aasx.launch_explorer import check_explorer_status
        import psutil
        
        # Get comprehensive status from launcher module
        status = check_explorer_status()
        
        # Check if running (additional process check)
        running = False
        pid = None
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                if 'aasxpackageexplorer' in proc_name or 'wine' in proc_name:
                    running = True
                    pid = proc_info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Add process status to the result
        status["running"] = running
        status["pid"] = pid
        status["success"] = True
        
        return status
        
    except ImportError as e:
        return {
            "success": False,
            "error": f"Launcher module not available: {str(e)}"
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