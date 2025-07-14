# GUI Vector Database Management Guide

This guide explains how to manage the **Global Vector Database** using the web interface, perfect for users who prefer graphical tools over command-line operations.

## 🎯 **What is the Global Vector Database?**

The Global Vector Database is a **persistent Qdrant server** that stores embeddings from all processed AASX files. It enables:

- **Cross-file semantic search** across all processed data
- **AI-powered analysis** with context from multiple files
- **Persistent storage** that survives server restarts
- **Accumulated knowledge** from all ETL pipeline runs

## 🚀 **Accessing Vector Database Management**

### Step 1: Navigate to AI/RAG System
1. Open your web browser
2. Go to `http://localhost:8000/ai-rag`
3. You'll see the AI/RAG System interface

### Step 2: Find Vector Database Section
Scroll down to the **"Global Vector Database Management"** section, which includes:

- **Database Information** panel (left side)
- **Backup Operations** panel (right side)

## 📊 **Database Information Panel**

### **What You'll See:**
- **Total Collections**: Number of all collections in the database
- **Database Type**: Qdrant (the vector database engine)
- **Status**: Connected/Not Connected indicator
- **Last Updated**: When the information was last refreshed
- **AASX Collections**: Number of collections from AASX files

### **How to Use:**
1. **View Current Status**: Information loads automatically when you visit the page
2. **Refresh Information**: Click the **"Refresh Info"** button to get the latest data
3. **Monitor Growth**: Watch the collection count increase as you process more AASX files

### **Example Display:**
```
✅ Database Information
Total Collections: 156
Database Type: Qdrant
Status: Connected
Last Updated: Now
Collections from all ETL runs are accumulated globally
```

## 💾 **Backup Operations Panel**

### **Available Backup Options:**

#### 1. **Metadata Backup** (Fast & Small)
- **What it includes**: Collection names, structure, and metadata
- **Size**: Usually a few MB
- **Speed**: Very fast (seconds)
- **Use case**: Quick backup for documentation

#### 2. **Full Backup** (Complete & Large)
- **What it includes**: All metadata + actual vector data
- **Size**: Can be hundreds of MB depending on data
- **Speed**: Slower (minutes)
- **Use case**: Complete backup for disaster recovery

#### 3. **Backup History** (View Previous Backups)
- **What it shows**: List of recent backups with details
- **Information**: Timestamp, type, size, collection count
- **Use case**: Track backup history and manage storage

### **How to Create Backups:**

#### **Step 1: Choose Backup Type**
- Click **"Create Metadata Backup"** for quick backup
- Click **"Create Full Backup"** for complete backup

#### **Step 2: Monitor Progress**
- A loading spinner appears: "Creating [type] backup... Please wait."
- The process runs in the background
- You can continue using other features while backup runs

#### **Step 3: View Results**
When complete, you'll see:
```
✅ Backup Created Successfully!
Location: backups/vector_db_20250711_143022
Size: 45.67 MB
Collections: 156
Backup completed at 2025-07-11T14:30:22.123456
```

### **How to View Backup History:**

1. Click **"Backup History"** button
2. View list of recent backups:
   ```
   📋 Recent Backups:
   • 2025-07-11T14:30:22 - Type: metadata | Size: 2.34 MB | Collections: 156
   • 2025-07-11T10:15:45 - Type: full | Size: 45.67 MB | Collections: 156
   • 2025-07-10T16:20:33 - Type: metadata | Size: 2.12 MB | Collections: 142
   ```

## 🔍 **Understanding the Data**

### **Collection Naming Convention:**
Collections follow this pattern: `aasx_[filename]_[entity_type]`

**Examples:**
- `aasx_additive-manufacturing-3d-printer_converted_assets`
- `aasx_hydrogen-filling-station_converted_submodels`
- `aasx_smart-grid-substation_converted_documents`

### **What Each Collection Contains:**
- **Assets**: Physical equipment and devices
- **Submodels**: Technical specifications and data
- **Documents**: Related files and documentation

### **Global Accumulation:**
- Each ETL run adds new collections
- Existing collections are updated (not duplicated)
- All data persists across server restarts
- Search works across all processed files

## 🚨 **Troubleshooting**

### **Common Issues and Solutions:**

#### **1. "Not Connected" Status**
**Problem**: Vector database shows as disconnected
**Solutions**:
- Check if Qdrant server is running: `curl http://localhost:6333`
- Restart the Qdrant server
- Check firewall settings

#### **2. Backup Fails**
**Problem**: Backup operation returns error
**Solutions**:
- Check disk space in the project directory
- Ensure write permissions to `backups/` folder
- Try metadata backup first (smaller, faster)

#### **3. No Collections Found**
**Problem**: Database shows 0 collections
**Solutions**:
- Run ETL pipeline on some AASX files first
- Check if vector database export is enabled in ETL config
- Verify Qdrant server is accessible

#### **4. Large Backup Sizes**
**Problem**: Full backups are very large
**Solutions**:
- Use metadata backups for regular operations
- Only use full backups for disaster recovery
- Consider cleaning old backups periodically

## 📈 **Best Practices**

### **Regular Maintenance:**
1. **Weekly**: Create metadata backup
2. **Monthly**: Create full backup
3. **Monitor**: Check collection count growth
4. **Clean**: Remove old backups if needed

### **Performance Tips:**
1. **Use metadata backups** for regular operations
2. **Schedule backups** during low-usage periods
3. **Monitor disk space** in backup directory
4. **Keep recent backups** and archive older ones

### **Security Considerations:**
1. **Backup location**: Backups are stored locally in `backups/` folder
2. **Access control**: Ensure only authorized users can access backup files
3. **Encryption**: Consider encrypting backup files for sensitive data
4. **Offsite storage**: Copy important backups to external storage

## 🔗 **Related Documentation**

- **[ETL Pipeline Guide](AASX_ETL_PIPELINE.md)** - How data gets into the vector database
- **[AI/RAG System Guide](AAS_INTEGRATION.md)** - Using the vector database for AI analysis
- **[Command Line Backup](scripts/backup_vector_db.py)** - Advanced backup options
- **[Configuration Guide](CONFIGURATION.md)** - Vector database settings

## 📞 **Getting Help**

### **If You Need Assistance:**
1. **Check the status indicators** in the GUI
2. **Review error messages** in the backup status panel
3. **Check server logs** for detailed error information
4. **Try the command-line backup script** for advanced troubleshooting

### **Useful Commands (for advanced users):**
```bash
# Check Qdrant server status
curl http://localhost:6333/collections

# View backup directory
ls -la backups/

# Check disk space
df -h backups/
```

---

**Last Updated**: July 2025  
**GUI Version**: 1.0.0  
**Compatible with**: AASX Digital Twin Analytics Framework v1.0.0 