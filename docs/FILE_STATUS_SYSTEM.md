# 📋 File Status System

This document describes the file status system used in the AAS Data Modeling platform to track the processing state of uploaded AASX files.

## 🎯 Overview

The file status system provides clear visibility into the processing state of each uploaded AASX file, allowing users to understand which files have been processed and which are still pending.

## 📊 Status Types

### 1. **Not Processed** (`not_processed`)
- **Badge Color**: Gray (`bg-secondary`)
- **Description**: File has been uploaded but not processed through the ETL pipeline yet
- **Action Required**: Run ETL processing to extract and transform the data
- **Example**: Newly uploaded files that haven't been processed

### 2. **Processing** (`processing`)
- **Badge Color**: Yellow (`bg-warning`)
- **Description**: File is currently being processed through the ETL pipeline
- **Action Required**: Wait for processing to complete
- **Example**: Files currently running through extract, transform, and load phases

### 3. **Completed** (`completed`)
- **Badge Color**: Green (`bg-success`)
- **Description**: File has been successfully processed through the ETL pipeline
- **Action Required**: None - file is ready for use
- **Example**: Files that have been processed and have output data available

### 4. **Error** (`error`)
- **Badge Color**: Red (`bg-danger`)
- **Description**: File processing failed due to an error
- **Action Required**: Review error details and retry processing
- **Example**: Files with parsing errors, missing dependencies, or processing failures

### 5. **Failed** (`failed`)
- **Badge Color**: Red (`bg-danger`)
- **Description**: File processing failed (alternative to 'error' status)
- **Action Required**: Review failure details and retry processing
- **Example**: Files that couldn't be processed due to system issues

### 6. **Queued** (`queued`)
- **Badge Color**: Blue (`bg-info`)
- **Description**: File is queued for processing
- **Action Required**: Wait for processing to begin
- **Example**: Files waiting in a processing queue

## 🔄 Status Transitions

The typical status flow for a file is:

```
Upload → Not Processed → Processing → Completed
                              ↓
                           Error/Failed
```

### Detailed Flow:
1. **Upload**: File is uploaded to the system
2. **Not Processed**: File is ready for ETL processing
3. **Processing**: ETL pipeline is actively processing the file
4. **Completed**: Processing successful, output data available
5. **Error/Failed**: Processing failed (can retry from Not Processed)

## 💾 Data Storage

### In-Memory Database
File statuses are stored in the `FILES_DB` dictionary in `webapp/aasx/routes.py`:

```python
FILES_DB = {
    "file_id": {
        "id": "file_id",
        "filename": "processed_filename.aasx",
        "original_filename": "original_filename.aasx",
        "project_id": "project_id",
        "filepath": "path/to/file.aasx",
        "size": 1234567,
        "upload_date": "2025-01-14T10:30:00",
        "description": "File description",
        "status": "not_processed",  # Current status
        "processing_result": None   # Processing results when completed
    }
}
```

### Persistent Storage
File statuses are also persisted to project-specific JSON files:

```
data/projects/{project_id}/files.json
```

## 🎨 Frontend Display

### Status Badges
The frontend displays file statuses using Bootstrap badges with appropriate colors:

```html
<span class="badge bg-secondary">Not Processed</span>
<span class="badge bg-warning">Processing</span>
<span class="badge bg-success">Completed</span>
<span class="badge bg-danger">Error</span>
```

### Status Mapping
The JavaScript frontend maps status values to display labels:

```javascript
const statusMap = {
    'not_processed': {
        label: 'Not Processed',
        badgeClass: 'bg-secondary',
        description: 'File has been uploaded but not processed yet'
    },
    'processing': {
        label: 'Processing',
        badgeClass: 'bg-warning',
        description: 'File is currently being processed'
    },
    'completed': {
        label: 'Completed',
        badgeClass: 'bg-success',
        description: 'File has been processed successfully'
    },
    // ... other statuses
};
```

## 🔧 Backend Management

### Status Updates
File statuses are updated during ETL processing in `webapp/aasx/routes.py`:

```python
# Update status to processing
file_info['status'] = 'processing'
FILES_DB[file_id] = file_info

# Process file through ETL pipeline
result = pipeline.process_aasx_file(file_path)

# Update status based on result
file_info['status'] = 'completed' if result['status'] == 'completed' else 'error'
file_info['processing_result'] = result
FILES_DB[file_id] = file_info
```

### Project Persistence
When file statuses are updated, the project is automatically saved to the filesystem:

```python
from webapp.aasx.routes import save_project_to_filesystem

# Save project after status update
save_project_to_filesystem(project_id)
```

## 🛠️ Management Scripts

### Check File Status
```bash
python scripts/check_file_status.py
```

### Update File Status
```bash
python scripts/update_file_status.py
```

### Update Status Terminology
```bash
python scripts/update_status_terminology.py
```

## 📈 Recent Changes

### Status Terminology Update (2025-01-14)
- **Before**: Files used "uploaded" status for unprocessed files
- **After**: Files now use "not_processed" status for unprocessed files
- **Reason**: More descriptive and clear terminology
- **Impact**: Better user understanding of file processing state

### Migration
The system automatically handles the transition:
- New files are created with "not_processed" status
- Existing "uploaded" statuses are mapped to "not_processed" in the frontend
- Migration scripts are available to update existing data

## 🎯 Best Practices

### 1. **Status Consistency**
- Always update file status when processing begins/ends
- Include processing results for completed files
- Handle error cases gracefully

### 2. **User Experience**
- Use clear, descriptive status labels
- Provide appropriate visual indicators (colors, icons)
- Include helpful descriptions for each status

### 3. **Data Integrity**
- Persist status changes to filesystem
- Include timestamps for status changes
- Maintain processing result history

### 4. **Error Handling**
- Distinguish between different types of failures
- Provide actionable error messages
- Allow retry mechanisms for failed files

## 🔍 Troubleshooting

### Common Issues

#### Status Not Updating
- Check if file exists in `FILES_DB`
- Verify project persistence is working
- Check for JavaScript errors in frontend

#### Status Display Issues
- Verify status mapping in frontend JavaScript
- Check badge CSS classes
- Ensure status values match expected format

#### Processing Stuck
- Check ETL pipeline logs
- Verify file paths are correct
- Check for system resource issues

### Debug Commands
```bash
# Check all file statuses
python scripts/check_file_status.py

# Update specific file status
python scripts/update_file_status.py "filename.aasx" "completed"

# View ETL pipeline logs
tail -f logs/etl_pipeline.log
``` 