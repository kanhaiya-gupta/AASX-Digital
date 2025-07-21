# Wine Integration for AASX Package Explorer

## Overview

This document describes the Wine integration that enables the Windows-based AASX Package Explorer to run in Linux Docker containers. This allows the external Windows software to be fully integrated into the AASX Digital Twin Analytics Framework.

## 🍷 What is Wine?

**Wine** (Wine Is Not an Emulator) is a compatibility layer that allows Windows applications to run on Unix-like systems (Linux, macOS). It translates Windows API calls into POSIX calls, enabling Windows software to run natively on Linux.

## 🏗️ Architecture

### Integration Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container (Linux)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   FastAPI App   │  │  .NET Processor │  │     Wine     │ │
│  │   (Python)      │  │   (C#/.NET)     │  │   (Windows   │ │
│  │                 │  │                 │  │  Compatibility│ │
│  └─────────────────┘  └─────────────────┘  │    Layer)    │ │
│                                           └──────────────┘ │
│                                           ┌──────────────┐ │
│                                           │ AASX Package │ │
│                                           │  Explorer    │ │
│                                           │  (Windows    │ │
│                                           │  .NET App)   │ │
│                                           └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- ✅ **Cross-Platform Compatibility**: Windows app runs on Linux containers
- ✅ **Full Integration**: Seamless integration with web interface
- ✅ **Performance**: Native-like performance with Wine
- ✅ **GUI Support**: Full graphical interface support
- ✅ **File System Access**: Direct access to host file system

## 🚀 Implementation Details

### Dockerfile Updates

The Dockerfile has been enhanced to include Wine:

```dockerfile
# Install Wine for Windows application support
RUN apt-get update && apt-get install -y \
    wine64 \
    wine32 \
    winbind \
    cabextract

# Install Wine Mono and Gecko for better Windows application support
RUN wget -qO- https://dl.winehq.org/wine/wine-mono/7.4.0/wine-mono-7.4.0-x86.msi | wine msiexec /i /quiet \
    && wget -qO- https://dl.winehq.org/wine/wine-gecko/2.47.3/wine-gecko-2.47.3-x86.msi | wine msiexec /i /quiet

# Copy AASX Package Explorer Windows application
COPY AasxPackageExplorer/ /app/AasxPackageExplorer/

# Set Wine environment variables
ENV WINEARCH=win64
ENV WINEPREFIX=/app/.wine
ENV DISPLAY=:99
```

### Launcher Script Updates

The launcher script (`src/aasx/launch_explorer.py`) now supports both native Windows and Wine:

```python
def launch_explorer(silent: bool = False) -> Dict[str, Any]:
    # Determine launch method based on platform
    current_platform = platform.system()
    
    if current_platform == "Windows":
        # Native Windows launch
        return launch_native_windows(explorer_path, silent, result)
    else:
        # Linux/macOS with Wine
        return launch_with_wine(explorer_path, silent, result)
```

### Wine Launch Function

```python
def launch_with_wine(explorer_path: Path, silent: bool, result: Dict[str, Any]) -> Dict[str, Any]:
    # Set Wine environment variables
    env = os.environ.copy()
    env['WINEARCH'] = 'win64'
    env['WINEPREFIX'] = str(get_project_root() / '.wine')
    env['DISPLAY'] = ':99'
    
    # Launch with Wine
    process = subprocess.Popen(
        ["wine", str(explorer_path)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WINEARCH` | Wine architecture | `win64` |
| `WINEPREFIX` | Wine prefix directory | `/app/.wine` |
| `DISPLAY` | X11 display | `:99` |

### Volume Mounts

The Docker Compose file includes the AASX Package Explorer volume mount:

```yaml
volumes:
  - ../../AasxPackageExplorer:/app/AasxPackageExplorer
```

## 🧪 Testing

### Wine Integration Test

Run the comprehensive Wine integration test:

```bash
# Test Wine integration
python scripts/test_wine_integration.py

# Test in Docker container
docker exec aasx-digital-webapp python scripts/test_wine_integration.py
```

### Test Components

1. **Wine Installation**: Verify Wine is properly installed
2. **Wine Configuration**: Check Wine configuration
3. **AASX Explorer Files**: Verify Windows application files
4. **Display Environment**: Check GUI display setup
5. **Wine AASX Launch**: Test actual application launch

## 🖥️ GUI Access

### Container GUI Options

#### Option 1: X11 Forwarding (Recommended for Development)

```bash
# Run container with X11 forwarding
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd):/app \
  aasx-digital-webapp

# Allow X11 connections
xhost +local:docker
```

#### Option 2: VNC Server (Recommended for Production)

```bash
# Install VNC server in container
RUN apt-get install -y tightvncserver

# Start VNC server
vncserver :99 -geometry 1920x1080 -depth 24
```

#### Option 3: Headless Mode (No GUI)

The application can run in headless mode for processing tasks without GUI access.

## 📊 Performance Considerations

### Wine Performance

- **CPU**: ~10-20% overhead compared to native Windows
- **Memory**: Additional ~100-200MB for Wine runtime
- **Disk**: ~500MB for Wine installation
- **GUI**: Near-native performance with proper display setup

### Optimization Tips

1. **Wine Prefix**: Use dedicated Wine prefix for better isolation
2. **Display**: Use X11 forwarding for best GUI performance
3. **Memory**: Monitor Wine memory usage in production
4. **Caching**: Wine caches improve subsequent launches

## 🔒 Security Considerations

### Container Security

- **Non-root User**: Wine runs under non-root user `aasx`
- **File Permissions**: Proper permissions set for Wine directories
- **Network Isolation**: Wine applications run within container network
- **Resource Limits**: Docker resource limits apply to Wine processes

### Wine Security

- **Sandboxing**: Wine provides application sandboxing
- **File Access**: Limited to mounted volumes
- **Network Access**: Controlled through container networking

## 🚨 Troubleshooting

### Common Issues

#### Wine Not Found
```bash
# Check Wine installation
docker exec aasx-digital-webapp wine --version

# Reinstall Wine if needed
docker exec aasx-digital-webapp apt-get update && apt-get install -y wine64
```

#### GUI Not Visible
```bash
# Check display environment
docker exec aasx-digital-webapp echo $DISPLAY

# Set display for X11 forwarding
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ...
```

#### AASX Explorer Not Found
```bash
# Check file existence
docker exec aasx-digital-webapp ls -la /app/AasxPackageExplorer/

# Verify volume mount
docker exec aasx-digital-webapp mount | grep AasxPackageExplorer
```

#### Wine Launch Fails
```bash
# Check Wine logs
docker exec aasx-digital-webapp wine --version

# Test with debug output
docker exec aasx-digital-webapp WINEDEBUG=+all wine /app/AasxPackageExplorer/AasxPackageExplorer.exe
```

### Debug Commands

```bash
# Wine configuration
docker exec aasx-digital-webapp winecfg

# Wine registry editor
docker exec aasx-digital-webapp regedit

# Wine debug output
docker exec aasx-digital-webapp WINEDEBUG=+all wine /app/AasxPackageExplorer/AasxPackageExplorer.exe

# Check Wine processes
docker exec aasx-digital-webapp ps aux | grep wine
```

## 📈 Monitoring

### Health Checks

The deployment script includes Wine health checks:

```bash
# Test Wine availability
docker exec aasx-digital-webapp wine --version

# Test AASX Explorer files
docker exec aasx-digital-webapp ls -la /app/AasxPackageExplorer/AasxPackageExplorer.exe

# Test Wine integration
docker exec aasx-digital-webapp python scripts/test_wine_integration.py
```

### Logging

Monitor Wine and AASX Explorer logs:

```bash
# Container logs
docker logs aasx-digital-webapp

# Wine logs (if enabled)
docker exec aasx-digital-webapp cat ~/.wine/dosdevices/c:/windows/system32/wine.log
```

## 🎯 Usage Examples

### Web Interface Launch

1. **Access Web Interface**: Navigate to `http://localhost:8000`
2. **Click Launch Button**: Use "Launch AASX Package Explorer" button
3. **Automatic Detection**: System detects platform and uses appropriate method
4. **GUI Access**: Application launches with GUI (if display configured)

### Command Line Launch

```bash
# Direct launch
python src/aasx/launch_explorer.py

# Silent launch (for scripts)
python -c "from src.aasx.launch_explorer import launch_explorer; launch_explorer(silent=True)"
```

### Docker Container Launch

```bash
# Launch from container
docker exec aasx-digital-webapp python src/aasx/launch_explorer.py

# Launch with X11 forwarding
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd):/app \
  aasx-digital-webapp \
  python src/aasx/launch_explorer.py
```

## 🔄 Integration with Framework

### Web Interface Integration

The Wine integration is seamlessly integrated into the web interface:

- **Automatic Detection**: Platform detection and method selection
- **Error Handling**: Comprehensive error handling and user feedback
- **Status Monitoring**: Real-time status checking
- **Fallback Options**: Web-based alternatives when Wine unavailable

### API Endpoints

```python
# Launch AASX Explorer
POST /aasx-explorer/launch

# Check status
GET /aasx-explorer/status

# Download application
GET /aasx-explorer/download
```

## 📋 Requirements

### System Requirements

- **Docker**: Version 20.10+
- **Linux Host**: Ubuntu 20.04+ recommended
- **Memory**: Additional 1GB for Wine
- **Storage**: Additional 1GB for Wine and Windows app

### Wine Requirements

- **Wine**: Version 6.0+
- **Wine Mono**: .NET Framework compatibility
- **Wine Gecko**: Internet Explorer compatibility
- **X11**: For GUI display (optional)

## 🎉 Benefits

### Cross-Platform Compatibility

- ✅ **Windows Apps on Linux**: Run Windows software in Linux containers
- ✅ **Docker Integration**: Seamless integration with Docker ecosystem
- ✅ **Cloud Deployment**: Deploy Windows apps to Linux cloud environments
- ✅ **Development Consistency**: Same environment across platforms

### External Software Integration

- ✅ **Third-Party Tools**: Integrate external Windows software
- ✅ **No Rewriting**: Use existing Windows applications as-is
- ✅ **Full Functionality**: Maintain all original features
- ✅ **Future-Proof**: Support for new Windows applications

## 🔮 Future Enhancements

### Planned Improvements

1. **Performance Optimization**: Wine performance tuning
2. **GUI Improvements**: Better display integration
3. **Security Hardening**: Enhanced security measures
4. **Monitoring**: Advanced monitoring and alerting
5. **Automation**: Automated Wine setup and configuration

### Alternative Approaches

1. **Web-Based Viewer**: Pure web-based AASX viewer
2. **Native Ports**: Native Linux ports of Windows applications
3. **Virtual Machines**: Full VM integration for Windows apps
4. **API Integration**: Direct API integration with Windows services

## 📚 References

- [Wine Official Documentation](https://wiki.winehq.org/)
- [Wine Installation Guide](https://wiki.winehq.org/Download)
- [Docker X11 Forwarding](https://wiki.qt.io/Building_Qt_6_from_Git/Docker)
- [AASX Package Explorer](https://github.com/admin-shell-io/aasx-package-explorer)

---

This Wine integration provides a robust solution for running the external Windows AASX Package Explorer in Linux Docker containers, enabling full cross-platform compatibility while maintaining all original functionality. 