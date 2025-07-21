# AAS Processor Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting for the AAS processor diagnostic system. It covers common issues, diagnostic procedures, and solutions for AASX processing problems.

## Quick Start

### Basic Diagnostic

```bash
# Diagnose a single AASX file
python scripts/diagnose_aas_processor.py path/to/file.aasx

# Diagnose with verbose output
python scripts/diagnose_aas_processor.py path/to/file.aasx --verbose

# Generate JSON output
python scripts/diagnose_aas_processor.py path/to/file.aasx --json

# Save report to file
python scripts/diagnose_aas_processor.py path/to/file.aasx --output report.txt
```

### Batch Processing

```bash
# Diagnose all AASX files in a directory
python scripts/diagnose_aas_processor.py path/to/directory --batch

# Compare two files
python scripts/diagnose_aas_processor.py --compare file1.aasx file2.aasx
```

## Common Issues and Solutions

### 1. Empty Asset/Submodel IDs

**Problem**: Assets or submodels are extracted but have empty IDs.

**Symptoms**:
- `assets_without_ids > 0` in diagnostic output
- `submodels_without_ids > 0` in diagnostic output
- Empty ID fields in JSON/YAML output

**Root Causes**:
- AAS version not properly detected
- XML namespace issues
- Incorrect extraction method used
- Malformed XML structure

**Solutions**:

#### A. Check AAS Version Detection
```bash
# Run diagnostic to check version detection
python scripts/diagnose_aas_processor.py file.aasx --verbose
```

Look for:
- `AAS Version: unknown` - indicates version detection failure
- Missing namespaces in output
- XML parsing errors

#### B. Update Version Detection
If version is `unknown`, check the XML structure:

```xml
<!-- AAS 3.0 -->
<aas:assetAdministrationShell xmlns:aas="http://www.admin-shell.io/aas/3/0">

<!-- AAS 2.0 -->
<aas:assetAdministrationShell xmlns:aas="http://www.admin-shell.io/aas/2/0">

<!-- AAS 1.0 -->
<aas:assetAdministrationShell xmlns:aas="http://www.admin-shell.io/aas/1/0">
```

#### C. Fix Namespace Issues
Update `AasProcessor.cs` to handle new namespaces:

```csharp
private bool IsAasNamespace(string namespaceUri)
{
    if (string.IsNullOrEmpty(namespaceUri))
        return false;
    
    return namespaceUri.Contains("admin-shell.io/aas") ||
           namespaceUri.Contains("aas:") ||
           namespaceUri.Contains("aas3") ||
           namespaceUri.Contains("aas2") ||
           namespaceUri.Contains("aas1");
}
```

#### D. Check Extraction Method Priority
Ensure version-specific extraction runs before generic extraction:

```csharp
// First, try version-specific extraction
var version = DetectAasVersion(doc);
switch (version)
{
    case "3.0":
        ExtractAas30Data(doc, nsManager, assets, submodels, sourceFile);
        break;
    case "2.0":
        ExtractAas20Data(doc, nsManager, assets, submodels, sourceFile);
        break;
    // ... other versions
}

// Only fall back to generic if no data found
if (assets.Count == 0 && submodels.Count == 0)
{
    ExtractGenericAasData(doc, assets, submodels, sourceFile);
}
```

### 2. Missing Embedded Files

**Problem**: Documents, images, or other files are not extracted.

**Symptoms**:
- `total_files: 0` in diagnostic output
- Missing files in output directories
- Empty documents/images arrays

**Root Causes**:
- AASX structure issues
- File path problems
- Extraction logic errors

**Solutions**:

#### A. Check AASX Structure
```bash
# Analyze AASX structure
python scripts/diagnose_aas_processor.py file.aasx --verbose
```

Look for:
- `is_valid_zip: false` - indicates corrupted AASX
- Missing file types in `file_types` section
- Files listed but not extracted

#### B. Verify File Extraction Logic
Check that the .NET processor extracts all file types:

```csharp
private void ExtractAllFiles(ZipArchive archive, List<object> documents, 
                            List<object> images, List<object> otherFiles)
{
    foreach (var entry in archive.Entries)
    {
        var extension = Path.GetExtension(entry.Name).ToLower();
        
        if (IsDocumentFile(extension))
            documents.Add(new { filename = entry.FullName, size = entry.Length, type = extension });
        else if (IsImageFile(extension))
            images.Add(new { filename = entry.FullName, size = entry.Length, type = extension });
        else
            otherFiles.Add(new { filename = entry.FullName, size = entry.Length, type = extension });
    }
}
```

### 3. XML Parsing Errors

**Problem**: XML files cannot be parsed or contain errors.

**Symptoms**:
- `xml_errors` array contains errors
- Processing fails with XML exceptions
- Malformed XML structure

**Root Causes**:
- Invalid XML syntax
- Encoding issues
- Namespace conflicts

**Solutions**:

#### A. Check XML Validity
```bash
# Use diagnostic to check XML errors
python scripts/diagnose_aas_processor.py file.aasx --verbose
```

#### B. Fix Encoding Issues
Update XML loading to handle encoding:

```csharp
var doc = new XmlDocument();
doc.LoadXml(xmlContent); // Try UTF-8 first

// If that fails, try with encoding detection
try
{
    doc.LoadXml(xmlContent);
}
catch
{
    var bytes = Encoding.Default.GetBytes(xmlContent);
    var utf8Content = Encoding.UTF8.GetString(bytes);
    doc.LoadXml(utf8Content);
}
```

#### C. Handle Namespace Conflicts
Use namespace-aware XML processing:

```csharp
private XmlNamespaceManager CreateNamespaceManager(XmlDocument doc)
{
    var nsManager = new XmlNamespaceManager(doc.NameTable);
    
    // Add common AAS namespaces
    nsManager.AddNamespace("aas", "http://www.admin-shell.io/aas/3/0");
    nsManager.AddNamespace("aas2", "http://www.admin-shell.io/aas/2/0");
    nsManager.AddNamespace("aas1", "http://www.admin-shell.io/aas/1/0");
    
    return nsManager;
}
```

### 4. Performance Issues

**Problem**: Processing takes too long or consumes too much memory.

**Symptoms**:
- `processing_time_seconds > 10` in diagnostic output
- High memory usage
- Timeout errors

**Root Causes**:
- Large AASX files
- Inefficient XML processing
- Memory leaks

**Solutions**:

#### A. Optimize XML Processing
Use streaming XML processing for large files:

```csharp
using (var reader = XmlReader.Create(new StringReader(xmlContent)))
{
    while (reader.Read())
    {
        if (reader.NodeType == XmlNodeType.Element)
        {
            // Process elements incrementally
        }
    }
}
```

#### B. Implement Caching
Cache processed results to avoid reprocessing:

```csharp
private static readonly Dictionary<string, object> _cache = new();

public object ProcessAasxFile(string filePath)
{
    var cacheKey = $"{filePath}_{File.GetLastWriteTime(filePath)}";
    
    if (_cache.TryGetValue(cacheKey, out var cached))
        return cached;
    
    var result = ProcessFile(filePath);
    _cache[cacheKey] = result;
    return result;
}
```

### 5. Version Compatibility Issues

**Problem**: Processor doesn't support new AAS versions.

**Symptoms**:
- `AAS Version: unknown` for valid files
- Missing data for new AAS versions
- Processing errors with new formats

**Root Causes**:
- Missing version detection patterns
- Outdated extraction methods
- New XML structures not handled

**Solutions**:

#### A. Add New Version Detection
Update version detection to include new patterns:

```csharp
private string DetectAasVersion(XmlDocument doc)
{
    // Check for AAS 4.0
    if (ContainsNamespace(doc, "http://www.admin-shell.io/aas/4/0") ||
        ContainsElement(doc, "aas4"))
        return "4.0";
    
    // Check for AAS 3.0
    if (ContainsNamespace(doc, "http://www.admin-shell.io/aas/3/0") ||
        ContainsElement(doc, "aas3"))
        return "3.0";
    
    // ... existing versions
}
```

#### B. Implement New Extraction Methods
Add extraction methods for new versions:

```csharp
private void ExtractAas40Data(XmlDocument doc, XmlNamespaceManager nsManager,
                             List<object> assets, List<object> submodels, string sourceFile)
{
    // Implement AAS 4.0 specific extraction
    var assetNodes = doc.SelectNodes("//aas4:asset", nsManager);
    var submodelNodes = doc.SelectNodes("//aas4:submodel", nsManager);
    
    // Extract data using AAS 4.0 structure
}
```

## Diagnostic Workflow

### Step 1: Initial Assessment
```bash
python scripts/diagnose_aas_processor.py file.aasx --verbose
```

### Step 2: Analyze Results
Look for:
- AAS version detection
- ID extraction status
- File extraction status
- Validation errors
- Performance metrics

### Step 3: Identify Root Cause
Based on diagnostic output, identify the specific issue:
- Version detection problems
- XML parsing errors
- ID extraction failures
- File extraction issues
- Performance problems

### Step 4: Apply Solution
Use the appropriate solution from the sections above.

### Step 5: Verify Fix
```bash
python scripts/diagnose_aas_processor.py file.aasx --verbose
```

Compare results to ensure the issue is resolved.

## Advanced Troubleshooting

### Custom Diagnostic Scripts

Create custom diagnostic scripts for specific issues:

```python
#!/usr/bin/env python3
"""Custom diagnostic for specific issue"""

import sys
from scripts.diagnose_aas_processor import AasProcessorDiagnostic

def custom_diagnostic(aasx_path):
    diagnostic = AasProcessorDiagnostic(verbose=True)
    result = diagnostic.diagnose_single_file(aasx_path)
    
    # Add custom analysis
    if result.aas_version == 'unknown':
        print("🔧 Custom fix: Adding new namespace patterns...")
        # Implement custom fix
    
    return result

if __name__ == "__main__":
    result = custom_diagnostic(sys.argv[1])
    print(result.recommendations)
```

### Batch Analysis

Analyze multiple files to identify patterns:

```bash
# Analyze all files in directory
python scripts/diagnose_aas_processor.py data/aasx/ --batch --json > analysis.json

# Find files with specific issues
jq '[.[] | select(.id_extraction_status.assets_without_ids > 0)]' analysis.json
```

### Integration with CI/CD

Add diagnostic checks to your build pipeline:

```yaml
# .github/workflows/aas-diagnostic.yml
name: AAS Diagnostic
on: [push, pull_request]

jobs:
  diagnostic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Diagnostic
        run: |
          python scripts/diagnose_aas_processor.py test-data/ --batch --json > diagnostic.json
          python scripts/check_diagnostic_results.py diagnostic.json
```

## Maintenance and Updates

### Regular Health Checks

Schedule regular diagnostic runs:

```bash
# Weekly health check
0 2 * * 1 python scripts/diagnose_aas_processor.py production-data/ --batch --output weekly-report.txt
```

### Version Compatibility Testing

Test new AAS versions:

```bash
# Test new AAS version
python scripts/diagnose_aas_processor.py new-version-sample.aasx --verbose
```

### Performance Monitoring

Monitor processing performance:

```bash
# Performance analysis
python scripts/diagnose_aas_processor.py large-file.aasx --json | jq '.performance_metrics'
```

## Support and Resources

### Documentation
- [AAS Specification](https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html)
- [AASX Package Explorer](https://github.com/admin-shell-io/aasx-package-explorer)
- [AAS Core Library](https://github.com/admin-shell-io/aas-core-library)

### Community
- [AAS Community Forum](https://www.plattform-i40.de/PI40/Navigation/EN/Community/community.html)
- [GitHub Issues](https://github.com/admin-shell-io/aasx-package-explorer/issues)

### Tools
- [AASX Package Explorer](https://github.com/admin-shell-io/aasx-package-explorer/releases)
- [AAS Validator](https://github.com/admin-shell-io/aas-validator)
- [AAS Registry](https://github.com/admin-shell-io/aas-registry)

## Conclusion

This troubleshooting guide provides a comprehensive approach to diagnosing and fixing AAS processor issues. The diagnostic script automates much of the analysis, making it easier to identify and resolve problems quickly.

For new AAS versions or complex issues, use the diagnostic workflow to systematically identify and fix problems. Regular health checks and performance monitoring help prevent issues before they become critical.

Remember to:
1. Always run diagnostics before making changes
2. Test fixes with multiple file types
3. Monitor performance after changes
4. Keep documentation updated
5. Contribute fixes back to the community 