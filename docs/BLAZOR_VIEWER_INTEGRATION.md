# Blazor Viewer Integration Guide

## Overview

This document describes the integration of the Blazor AASX Viewer into the AASX Digital Twin Analytics Framework, including fixes applied and troubleshooting procedures.

## Architecture

The Blazor viewer is integrated as a separate container service that:
- Loads AASX files on-demand via REST API calls
- Uses hierarchical project-based file paths (e.g., `project-id/filename.aasx`)
- Displays AASX data in a tree structure
- Integrates through nginx reverse proxy

### Service Configuration
- **Container**: `aasx-blazor`
- **Port**: 5001 (internal)
- **External Access**: `https://www.aasx-digital.de/aasx-viewer/`
- **Data Source**: `./data/projects/` (mounted from host)

## Key Features Implemented

### 1. On-Demand File Loading
- Files loaded only when requested via URL parameter
- Uses `Program.LoadPackageByProjectPath<T>()` for project-based loading
- Supports hierarchical paths: `project-id/filename.aasx`

### 2. Duplicate Loading Prevention
- Tracks last loaded file to prevent duplicates
- Implements concurrent loading protection
- Clears tracking when loading different files

### 3. Direct Navigation
- Automatically navigates to Tree page after file loading
- Eliminates manual navigation steps
- Provides seamless user experience

### 4. Error Handling
- Gracefully handles corrupted or invalid AASX files
- Provides clear error messages in logs
- Continues operation even with file loading failures

## Issues Fixed

### 1. Duplicate File Loading
**Problem**: Multiple instances of same file loaded, creating duplicates.

**Solution**: 
- Added static tracking variables (`_lastLoadedFile`, `_isLoading`)
- Implemented duplicate checking before loading
- Added concurrent loading protection

**Result**: Each file loads only once.

### 2. Navigation Issues
**Problem**: Users had to manually click "AASX Model" to see data.

**Solution**:
- Added automatic navigation to Tree page (`/`) after successful loading
- Used `NavMan.NavigateTo("/", forceLoad: false)`

**Result**: Users land directly on data display page.

### 3. Missing LICENSE.TXT
**Problem**: Blazor viewer threw `FileNotFoundException` for missing LICENSE.TXT.

**Solution**:
- Created `server/LICENSE.TXT` with framework information

**Result**: Eliminated startup errors.

### 4. URL Parameter Processing
**Problem**: File parameters processed on incorrect URL paths.

**Solution**:
- Modified logic to process file parameters on any path
- Added proper URL parsing and validation

**Result**: Reliable file loading regardless of URL structure.

## Troubleshooting Guide

### Common Issues

#### 1. Blazor Viewer Not Loading Data
**Symptoms**: Page shows "Sorry, there's nothing at this address"

**Diagnosis**:
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs aasx-blazor -f
```

**Solutions**:
- Verify file exists in `./data/projects/project-id/filename.aasx`
- Check file permissions and integrity
- Restart Blazor container if needed

#### 2. Duplicate File Entries
**Symptoms**: Multiple identical entries in tree view

**Solutions**:
- Restart Blazor container to clear tracking state
- Check for navigation loops in URL processing

#### 3. Connection Refused Errors
**Symptoms**: "ERR_CONNECTION_REFUSED" when accessing viewer

**Solutions**:
- Restart Blazor container: `docker-compose restart aasx-blazor`
- Check container health and resource usage
- Verify nginx configuration

#### 4. File Loading Failures
**Common Errors**:
- `"End of Central Directory record could not be found"` - Corrupted AASX file
- `"Unable to find AASX origin"` - Invalid AASX structure
- `"Invalid project path format"` - Incorrect file path

**Solutions**:
- Verify AASX file integrity
- Check file path format: `project-id/filename.aasx`
- Replace corrupted files with valid AASX files

### Debugging Commands

#### Check Container Status
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml ps
```

#### View Real-time Logs
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs aasx-blazor -f
```

#### Restart Blazor Service
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml restart aasx-blazor
```

#### Rebuild Blazor Container
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop aasx-blazor
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml build aasx-blazor
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d aasx-blazor
```

## Implementation Details

### MainLayout.razor Key Code

```csharp
private static string _lastLoadedFile = null;
private static bool _isLoading = false;

private async Task LoadFileFromUrlParameter()
{
    if (_isLoading) return;
    
    var fileParam = query.Get("file");
    if (_lastLoadedFile == fileParam) return;
    
    var loadedPackage = Program.LoadPackageByProjectPath<Environment>(
        out bool success, out int packageIndex, fileParam);
    
    if (success)
    {
        _lastLoadedFile = fileParam;
        Program.signalNewData(2);
        NavMan.NavigateTo("/", forceLoad: false);
    }
}
```

### Nginx Configuration

```nginx
location /aasx-viewer/ {
    proxy_pass http://blazor_viewer/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Files to Edit for Future Issues

### Core Files for Blazor Viewer Problems

#### 1. Main Integration Logic
**File**: `server/src/AasxServerBlazor/Shared/MainLayout.razor`

**Edit for**:
- File loading problems
- Duplicate loading issues  
- Navigation problems
- URL parameter processing
- Error handling

**Key sections to modify**:
- `LoadFileFromUrlParameter()` method (lines ~350-400)
- `_lastLoadedFile` and `_isLoading` tracking variables
- Navigation logic (`NavMan.NavigateTo()`)

#### 2. Navigation and Display
**File**: `server/src/AasxServerBlazor/Shared/NavMenu.razor`

**Edit for**:
- Navigation menu changes
- Menu structure modifications
- Navigation links

**File**: `server/src/AasxServerBlazor/Pages/TreePage.razor`

**Edit for**:
- Data display issues
- Tree view problems
- Page layout changes
- Data rendering logic

#### 3. Reverse Proxy Configuration
**File**: `nginx/nginx.conf`

**Edit for**:
- Connection refused errors
- URL routing problems
- Static resource loading issues
- SSL/HTTPS problems

**Key sections to modify**:
- `/aasx-viewer/` location block (lines ~95-105)
- Blazor static resources routing
- Proxy headers and timeouts

### Problem → File Mapping

| Problem Type | Primary File | Secondary File |
|--------------|--------------|----------------|
| **View/Page Landing Issues** | `MainLayout.razor` | `TreePage.razor` |
| **File Loading Problems** | `MainLayout.razor` | - |
| **Duplicate Loading Issues** | `MainLayout.razor` | - |
| **Connection/Network Issues** | `nginx/nginx.conf` | - |
| **UI/Display Issues** | `TreePage.razor` | `Tree.razor` |
| **Navigation Menu Issues** | `NavMenu.razor` | - |

### Quick Edit Reference

#### Fix Navigation Issues
```csharp
// In MainLayout.razor - LoadFileFromUrlParameter() method
NavMan.NavigateTo("/", forceLoad: false); // Change path or forceLoad parameter
```

#### Fix Duplicate Loading
```csharp
// In MainLayout.razor - LoadFileFromUrlParameter() method
if (_lastLoadedFile == fileParam) return; // Modify duplicate checking logic
```

#### Fix Nginx Routing
```nginx
# In nginx.conf - /aasx-viewer/ location block
location /aasx-viewer/ {
    proxy_pass http://blazor_viewer/; # Check proxy target
    # Modify headers or timeouts as needed
}
```

#### Fix Display Issues
```csharp
// In TreePage.razor - Tree component section
<Tree @bind-ExpandedNodes="ExpandedNodes" @bind-SelectedNode="SelectedNode" 
      ChildSelector="@(item => item.Children)" ...>
```

### Edit Workflow

1. **Identify the problem** using logs:
   ```bash
   docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs aasx-blazor -f
   ```

2. **Locate the relevant file** from the mapping above

3. **Make targeted edits** to the specific sections

4. **Rebuild the container**:
   ```bash
   docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop aasx-blazor
   docker-compose -f manifests/framework/docker-compose.aasx-digital.yml build aasx-blazor
   docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d aasx-blazor
   ```

5. **Test the fix** and check logs

### Most Common Edits (90% of issues)

- **`server/src/AasxServerBlazor/Shared/MainLayout.razor`**: File loading, navigation, duplicate prevention
- **`nginx/nginx.conf`**: Connection, routing, proxy configuration

### Less Common Edits (10% of issues)

- **`server/src/AasxServerBlazor/Pages/TreePage.razor`**: Display and rendering issues
- **`server/src/AasxServerBlazor/Shared/NavMenu.razor`**: Navigation menu problems

## Testing

### Valid Test Cases
- Load existing AASX files: `Example_AAS_ServoDCMotor_21.aasx`
- Test duplicate loading prevention
- Verify navigation to data display page

### Invalid Test Cases
- Corrupted AASX files (should fail gracefully)
- Non-existent file paths (should show error)
- Invalid project IDs (should fail with clear message)

## Future Improvements

1. **Enhanced Error Handling**: User-friendly error messages in UI
2. **Performance Optimization**: File caching and loading indicators
3. **User Experience**: File search, filtering, and export capabilities
4. **Monitoring**: Structured logging and health checks

## Conclusion

The Blazor viewer integration provides a robust interface for viewing AASX files within the framework. The implemented solutions address common issues and provide a solid foundation for future enhancements. 