using System;
using System.IO;
using System.Text.Json;
using System.Collections.Generic;
using System.Linq;

namespace AasProcessor
{
    /// <summary>
    /// AASX Package Processor using official AasCore.Aas3.Package library
    /// </summary>
    public class AasProcessor
    {
        /// <summary>
        /// Process an AASX file and return structured data
        /// </summary>
        /// <param name="aasxFilePath">Path to the AASX file</param>
        /// <returns>JSON string containing processed AAS data</returns>
        public string ProcessAasxFile(string aasxFilePath)
        {
            try
            {
                if (!File.Exists(aasxFilePath))
                {
                    throw new FileNotFoundException($"AASX file not found: {aasxFilePath}");
                }

                // For now, we'll use basic ZIP processing since the AAS Core library
                // has namespace issues with .NET 6.0
                var result = ProcessAasxBasic(aasxFilePath);
                
                return JsonSerializer.Serialize(result, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
            catch (Exception ex)
            {
                var error = new
                {
                    error = ex.Message,
                    processing_method = "basic_zip_processing",
                    file_path = aasxFilePath,
                    processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
                };

                return JsonSerializer.Serialize(error, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
        }

        /// <summary>
        /// Basic AASX processing using ZIP file operations
        /// </summary>
        private object ProcessAasxBasic(string aasxFilePath)
        {
            var fileInfo = new FileInfo(aasxFilePath);
            var documents = new List<object>();
            var images = new List<object>();
            var otherFiles = new List<object>();
            var assets = new List<object>();
            var submodels = new List<object>();
            var jsonFiles = new List<string>();
            var xmlFiles = new List<string>();
            
            try
            {
                using (var zip = System.IO.Compression.ZipFile.OpenRead(aasxFilePath))
                {
                    // Extract all embedded files (documents, images, etc.)
                    foreach (var entry in zip.Entries)
                    {
                        Console.WriteLine($"Found entry: {entry.Name}");
                        
                        var extension = Path.GetExtension(entry.Name).ToLowerInvariant();
                        var entryInfo = new
                        {
                            filename = entry.FullName,
                            size = entry.Length,
                            type = extension
                        };
                        
                        // Categorize files
                        if (extension == ".pdf" || extension == ".doc" || extension == ".docx" || extension == ".txt")
                        {
                            documents.Add(entryInfo);
                            Console.WriteLine($"Added document: {entry.Name}");
                        }
                        else if (extension == ".jpg" || extension == ".jpeg" || extension == ".png" || extension == ".gif" || extension == ".bmp")
                        {
                            images.Add(entryInfo);
                            Console.WriteLine($"Added image: {entry.Name}");
                        }
                        else if (!entry.FullName.StartsWith("[Content_Types]") && !entry.FullName.Contains("_rels") && extension != ".xml" && extension != ".json")
                        {
                            otherFiles.Add(entryInfo);
                            Console.WriteLine($"Added other file: {entry.Name}");
                        }
                        
                        // Process JSON files for AAS data
                        if (entry.Name.EndsWith(".json"))
                        {
                            jsonFiles.Add(entry.Name);
                            Console.WriteLine($"Processing JSON file: {entry.Name}");
                            try
                            {
                                using (var stream = entry.Open())
                                using (var reader = new StreamReader(stream))
                                {
                                    var content = reader.ReadToEnd();
                                    var jsonData = JsonSerializer.Deserialize<JsonElement>(content);
                                    
                                    // Extract AAS data from JSON
                                    ExtractAasFromJson(jsonData, assets, submodels, entry.Name);
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error processing JSON {entry.Name}: {ex.Message}");
                            }
                        }
                        // Process XML files (AAS data)
                        else if (entry.Name.EndsWith(".xml") && !entry.Name.StartsWith("[Content_Types]"))
                        {
                            Console.WriteLine($"Found XML file: {entry.Name}");
                            // Check if it's an AAS XML file
                            if (entry.Name.Contains(".aas.xml") || entry.Name.Contains("/aas.xml") || entry.Name.Contains("\\aas.xml") || entry.Name.Contains("aas.xml"))
                            {
                                xmlFiles.Add(entry.Name);
                                Console.WriteLine($"Processing AAS XML file: {entry.Name}");
                                try
                                {
                                    using (var stream = entry.Open())
                                    using (var reader = new StreamReader(stream))
                                    {
                                        var content = reader.ReadToEnd();
                                        Console.WriteLine($"Processing XML file: {entry.Name}");
                                        
                                        // Extract AAS data from XML
                                        ExtractAasFromXml(content, assets, submodels, entry.Name);
                                    }
                                }
                                catch (Exception ex)
                                {
                                    Console.WriteLine($"Error processing XML {entry.Name}: {ex.Message}");
                                }
                            }
                            else
                            {
                                Console.WriteLine($"Skipping non-AAS XML file: {entry.Name}");
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing AASX file: {ex.Message}");
                return null;
            }

            return new
            {
                processing_method = "enhanced_zip_processing",
                file_path = aasxFilePath,
                file_size = fileInfo.Length,
                processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                libraries_used = new[] { "System.IO.Compression", "System.Text.Json", "System.Xml" },
                assets = assets,
                submodels = submodels,
                documents = documents,
                images = images,
                other_files = otherFiles,
                raw_data = new
                {
                    json_files = jsonFiles,
                    xml_files = xmlFiles
                }
            };
        }

        /// <summary>
        /// Process an AASX file with enhanced data extraction and save documents separately
        /// </summary>
        /// <param name="aasxFilePath">Path to the AASX file</param>
        /// <param name="outputPath">Path where to save the JSON and documents</param>
        /// <returns>JSON string containing processed AAS data</returns>
        public string ProcessAasxFileEnhanced(string aasxFilePath, string outputPath = null)
        {
            try
            {
                if (!File.Exists(aasxFilePath))
                {
                    throw new FileNotFoundException($"AASX file not found: {aasxFilePath}");
                }

                // Use enhanced processing with document extraction
                var result = ProcessAasxEnhanced(aasxFilePath, outputPath);
                
                return JsonSerializer.Serialize(result, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
            catch (Exception ex)
            {
                var error = new
                {
                    error = ex.Message,
                    processing_method = "enhanced_with_document_extraction",
                    file_path = aasxFilePath,
                    processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
                };

                return JsonSerializer.Serialize(error, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
        }

        /// <summary>
        /// Enhanced AASX processing with complete structure preservation
        /// </summary>
        private object ProcessAasxEnhanced(string aasxFilePath, string outputPath = null)
        {
            var fileInfo = new FileInfo(aasxFilePath);
            var documents = new List<object>();
            var images = new List<object>();
            var otherFiles = new List<object>();
            var assets = new List<object>();
            var submodels = new List<object>();
            var jsonFiles = new List<string>();
            var xmlFiles = new List<string>();
            
            // NEW: Enhanced data structures for complete preservation
            var aasXmlContent = new Dictionary<string, object>();
            var assetSubmodelRelationships = new List<object>();
            var fileRelationships = new List<object>();
            var aasxStructure = new Dictionary<string, object>();
            var embeddedFiles = new Dictionary<string, object>();
            var namespaces = new Dictionary<string, string>();
            var aasVersion = "UNKNOWN";
            
            try
            {
                using (var zip = System.IO.Compression.ZipFile.OpenRead(aasxFilePath))
                {
                    // Extract AASX structure information
                    aasxStructure["total_entries"] = zip.Entries.Count;
                    aasxStructure["compression_method"] = "DEFLATE";
                    
                    // Find AASX origin and relationships
                    var aasxOriginEntry = zip.Entries.FirstOrDefault(e => e.Name == "aasx-origin");
                    if (aasxOriginEntry != null)
                    {
                        using (var stream = aasxOriginEntry.Open())
                        using (var reader = new StreamReader(stream))
                        {
                            var originContent = reader.ReadToEnd();
                            aasxStructure["aasx_origin"] = originContent.Trim();
                        }
                    }
                    
                    var aasxOriginRelsEntry = zip.Entries.FirstOrDefault(e => e.Name == "aasx-origin.rels");
                    if (aasxOriginRelsEntry != null)
                    {
                        using (var stream = aasxOriginRelsEntry.Open())
                        using (var reader = new StreamReader(stream))
                        {
                            var relsContent = reader.ReadToEnd();
                            aasxStructure["aasx_origin_rels"] = relsContent;
                        }
                    }
                    
                    // Extract all embedded files with enhanced metadata
                    foreach (var entry in zip.Entries)
                    {
                        Console.WriteLine($"Found entry: {entry.Name}");
                        
                        var extension = Path.GetExtension(entry.Name).ToLowerInvariant();
                        var entryInfo = new
                        {
                            filename = entry.FullName,
                            size = entry.Length,
                            type = extension,
                            compression_method = "DEFLATE", // Default compression method
                            last_modified = entry.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                            crc32 = entry.Crc32.ToString("X8")
                        };
                        
                        // Store embedded file metadata and extract to documents directory
                        var fileMetadata = new
                        {
                            filename = entry.FullName,
                            size = entry.Length,
                            type = extension,
                            compression_method = "DEFLATE",
                            last_modified = entry.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                            crc32 = entry.Crc32.ToString("X8"),
                            is_directory = entry.FullName.EndsWith("/")
                        };
                        
                        embeddedFiles[entry.FullName] = fileMetadata;
                        
                        // Extract file to documents directory if output path is provided
                        if (!string.IsNullOrEmpty(outputPath) && !entry.FullName.EndsWith("/"))
                        {
                            try
                            {
                                var documentsDir = Path.Combine(Path.GetDirectoryName(outputPath) ?? ".", 
                                    Path.GetFileNameWithoutExtension(outputPath) + "_documents");
                                Directory.CreateDirectory(documentsDir);
                                
                                var targetPath = Path.Combine(documentsDir, entry.FullName);
                                var targetDir = Path.GetDirectoryName(targetPath);
                                if (!string.IsNullOrEmpty(targetDir))
                                {
                                    Directory.CreateDirectory(targetDir);
                                }
                                
                                using (var entryStream = entry.Open())
                                using (var fileStream = File.Create(targetPath))
                                {
                                    entryStream.CopyTo(fileStream);
                                }
                                
                                Console.WriteLine($"Extracted file: {entry.FullName} -> {targetPath}");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Warning: Could not extract {entry.FullName}: {ex.Message}");
                            }
                        }
                        
                        // Categorize files
                        if (extension == ".pdf" || extension == ".doc" || extension == ".docx" || extension == ".txt")
                        {
                            documents.Add(entryInfo);
                            Console.WriteLine($"Added document: {entry.Name}");
                        }
                        else if (extension == ".jpg" || extension == ".jpeg" || extension == ".png" || extension == ".gif" || extension == ".bmp")
                        {
                            images.Add(entryInfo);
                            Console.WriteLine($"Added image: {entry.Name}");
                        }
                        else if (!entry.FullName.StartsWith("[Content_Types]") && !entry.FullName.Contains("_rels") && extension != ".xml" && extension != ".json")
                        {
                            otherFiles.Add(entryInfo);
                            Console.WriteLine($"Added other file: {entry.Name}");
                        }
                        
                        // Process JSON files for AAS data
                        if (entry.Name.EndsWith(".json"))
                        {
                            jsonFiles.Add(entry.Name);
                            Console.WriteLine($"Processing JSON file: {entry.Name}");
                            try
                            {
                                using (var stream = entry.Open())
                                using (var reader = new StreamReader(stream))
                                {
                                    var content = reader.ReadToEnd();
                                    var jsonData = JsonSerializer.Deserialize<JsonElement>(content);
                                    
                                    // Store complete JSON content
                                    aasXmlContent[entry.Name] = new
                                    {
                                        format = "JSON",
                                        content = content,
                                        source_file = entry.Name
                                    };
                                    
                                    // Extract AAS data from JSON
                                    ExtractAasFromJsonEnhanced(jsonData, assets, submodels, entry.Name, assetSubmodelRelationships);
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error processing JSON {entry.Name}: {ex.Message}");
                            }
                        }
                        // Process XML files (AAS data)
                        else if (entry.Name.EndsWith(".xml") && !entry.Name.StartsWith("[Content_Types]"))
                        {
                            Console.WriteLine($"Found XML file: {entry.Name}");
                            // Check if it's an AAS XML file
                            if (entry.Name.Contains(".aas.xml") || entry.Name.Contains("/aas.xml") || entry.Name.Contains("\\aas.xml") || entry.Name.Contains("aas.xml"))
                            {
                                xmlFiles.Add(entry.Name);
                                Console.WriteLine($"Processing AAS XML file: {entry.Name}");
                                try
                                {
                                    using (var stream = entry.Open())
                                    using (var reader = new StreamReader(stream))
                                    {
                                        var content = reader.ReadToEnd();
                                        Console.WriteLine($"Processing XML file: {entry.Name}");
                                        
                                        // Store complete XML content
                                        aasXmlContent[entry.Name] = new
                                        {
                                            format = "XML",
                                            content = content,
                                            source_file = entry.Name
                                        };
                                        
                                        // Extract AAS data from XML with enhanced processing
                                        ExtractAasFromXmlEnhanced(content, assets, submodels, entry.Name, assetSubmodelRelationships, fileRelationships, ref aasVersion, namespaces);
                                    }
                                }
                                catch (Exception ex)
                                {
                                    Console.WriteLine($"Error processing XML {entry.Name}: {ex.Message}");
                                }
                            }
                            else
                            {
                                Console.WriteLine($"Skipping non-AAS XML file: {entry.Name}");
                            }
                        }
                        
                        // Process relationship files
                        if (entry.Name.EndsWith(".rels"))
                        {
                            try
                            {
                                using (var stream = entry.Open())
                                using (var reader = new StreamReader(stream))
                                {
                                    var relsContent = reader.ReadToEnd();
                                    aasxStructure[$"rels_{entry.Name.Replace(".rels", "")}"] = relsContent;
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error processing relationship file {entry.Name}: {ex.Message}");
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing AASX file: {ex.Message}");
                return null;
            }

            return new
            {
                // Enhanced metadata
                aasVersion = aasVersion,
                namespaces = namespaces,
                
                // Complete AAS XML content
                aasXmlContent = aasXmlContent,
                
                // Enhanced structure information
                aasxStructure = aasxStructure,
                
                // Relationships
                assetSubmodelRelationships = assetSubmodelRelationships,
                fileRelationships = fileRelationships,
                
                // Embedded files with complete metadata
                embeddedFiles = embeddedFiles,
                
                // Processing metadata
                processing_method = "enhanced_forward_processing",
                file_path = aasxFilePath,
                file_size = fileInfo.Length,
                processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                libraries_used = new[] { "System.IO.Compression", "System.Text.Json", "System.Xml" },
                
                // Legacy structure for compatibility
                assets = assets,
                submodels = submodels,
                documents = documents,
                images = images,
                other_files = otherFiles,
                raw_data = new
                {
                    json_files = jsonFiles,
                    xml_files = xmlFiles
                }
            };
        }

        private void ExtractAasFromJson(JsonElement jsonData, List<object> assets, List<object> submodels, string sourceFile)
        {
            // Try to extract AAS data from JSON
            if (jsonData.TryGetProperty("assetAdministrationShells", out var aasArray))
            {
                foreach (var aas in aasArray.EnumerateArray())
                {
                    var asset = new
                    {
                        id = GetJsonProperty(aas, "id"),
                        idShort = GetJsonProperty(aas, "idShort"),
                        description = GetDescription(aas),
                        kind = GetJsonProperty(aas, "kind"),
                        source = sourceFile,
                        format = "JSON"
                    };
                    assets.Add(asset);
                }
            }
            
            if (jsonData.TryGetProperty("submodels", out var submodelArray))
            {
                foreach (var submodel in submodelArray.EnumerateArray())
                {
                    var submodelData = new
                    {
                        id = GetJsonProperty(submodel, "id"),
                        idShort = GetJsonProperty(submodel, "idShort"),
                        description = GetDescription(submodel),
                        kind = GetJsonProperty(submodel, "kind"),
                        source = sourceFile,
                        format = "JSON"
                    };
                    submodels.Add(submodelData);
                }
            }
        }

        /// <summary>
        /// Enhanced AAS extraction from JSON with relationship tracking
        /// </summary>
        private void ExtractAasFromJsonEnhanced(JsonElement jsonData, List<object> assets, List<object> submodels, 
            string sourceFile, List<object> assetSubmodelRelationships)
        {
            // Try to extract AAS data from JSON
            if (jsonData.TryGetProperty("assetAdministrationShells", out var aasArray))
            {
                foreach (var aas in aasArray.EnumerateArray())
                {
                    var assetId = GetJsonProperty(aas, "id");
                    var asset = new
                    {
                        id = assetId,
                        idShort = GetJsonProperty(aas, "idShort"),
                        description = GetDescription(aas),
                        kind = GetJsonProperty(aas, "kind"),
                        source = sourceFile,
                        format = "JSON"
                    };
                    assets.Add(asset);
                    
                    // Track submodel relationships
                    if (aas.TryGetProperty("submodels", out var submodelRefs))
                    {
                        foreach (var submodelRef in submodelRefs.EnumerateArray())
                        {
                            var submodelId = GetJsonProperty(submodelRef, "keys");
                            if (!string.IsNullOrEmpty(submodelId))
                            {
                                assetSubmodelRelationships.Add(new
                                {
                                    asset_id = assetId,
                                    submodel_id = submodelId,
                                    relationship_type = "submodel_reference",
                                    source = sourceFile
                                });
                            }
                        }
                    }
                }
            }
            
            if (jsonData.TryGetProperty("submodels", out var submodelArray))
            {
                foreach (var submodel in submodelArray.EnumerateArray())
                {
                    var submodelData = new
                    {
                        id = GetJsonProperty(submodel, "id"),
                        idShort = GetJsonProperty(submodel, "idShort"),
                        description = GetDescription(submodel),
                        kind = GetJsonProperty(submodel, "kind"),
                        source = sourceFile,
                        format = "JSON"
                    };
                    submodels.Add(submodelData);
                }
            }
        }

        private void ExtractAasFromXml(string xmlContent, List<object> assets, List<object> submodels, string sourceFile)
        {
            try
            {
                var doc = new System.Xml.XmlDocument();
                doc.LoadXml(xmlContent);
                
                Console.WriteLine($"Processing XML file: {sourceFile}");
                
                // First, try version-specific extraction
                var version = DetectAasVersion(doc);
                Console.WriteLine($"Detected AAS version: {version}");
                
                var nsManager = CreateNamespaceManager(doc);
                
                switch (version)
                {
                    case "3.0":
                        ExtractAas30Data(doc, nsManager, assets, submodels, sourceFile);
                        break;
                    case "2.0":
                        ExtractAas20Data(doc, nsManager, assets, submodels, sourceFile);
                        break;
                    case "1.0":
                        ExtractAas10Data(doc, nsManager, assets, submodels, sourceFile);
                        break;
                    default:
                        Console.WriteLine($"Unknown AAS version: {version}, trying generic extraction...");
                        ExtractGenericAasData(doc, assets, submodels, sourceFile);
                        break;
                }
                
                // If no data found with version-specific extraction, fall back to generic
                if (assets.Count == 0 && submodels.Count == 0)
                {
                    Console.WriteLine("No data found with version-specific extraction, trying generic extraction...");
                    ExtractGenericAasData(doc, assets, submodels, sourceFile);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing XML: {ex.Message}");
            }
        }

        /// <summary>
        /// Enhanced AAS extraction from XML with complete relationship tracking
        /// </summary>
        private void ExtractAasFromXmlEnhanced(string xmlContent, List<object> assets, List<object> submodels, 
            string sourceFile, List<object> assetSubmodelRelationships, List<object> fileRelationships, 
            ref string aasVersion, Dictionary<string, string> namespaces)
        {
            try
            {
                var doc = new System.Xml.XmlDocument();
                doc.LoadXml(xmlContent);
                
                Console.WriteLine($"Processing XML file: {sourceFile}");
                
                // Detect AAS version and namespaces
                aasVersion = DetectAasVersion(doc);
                Console.WriteLine($"Detected AAS version: {aasVersion}");
                
                // Extract all namespaces
                ExtractAllNamespaces(doc, namespaces);
                
                var nsManager = CreateNamespaceManager(doc);
                
                // Extract with enhanced relationship tracking
                switch (aasVersion)
                {
                    case "3.0":
                        ExtractAas30DataEnhanced(doc, nsManager, assets, submodels, sourceFile, assetSubmodelRelationships, fileRelationships);
                        break;
                    case "2.0":
                        ExtractAas20DataEnhanced(doc, nsManager, assets, submodels, sourceFile, assetSubmodelRelationships, fileRelationships);
                        break;
                    case "1.0":
                        ExtractAas10DataEnhanced(doc, nsManager, assets, submodels, sourceFile, assetSubmodelRelationships, fileRelationships);
                        break;
                    default:
                        Console.WriteLine($"Unknown AAS version: {aasVersion}, trying generic extraction...");
                        ExtractGenericAasDataEnhanced(doc, assets, submodels, sourceFile, assetSubmodelRelationships, fileRelationships);
                        break;
                }
                
                // If no data found with version-specific extraction, fall back to generic
                if (assets.Count == 0 && submodels.Count == 0)
                {
                    Console.WriteLine("No data found with version-specific extraction, trying generic extraction...");
                    ExtractGenericAasDataEnhanced(doc, assets, submodels, sourceFile, assetSubmodelRelationships, fileRelationships);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing XML: {ex.Message}");
            }
        }

        private string DetectAasVersion(System.Xml.XmlDocument doc)
        {
            try
            {
                // Check root element for AAS version indicators
                var root = doc.DocumentElement;
                if (root != null)
                {
                    var rootName = root.Name.ToLower();
                    var rootNamespace = root.NamespaceURI;

                    if (rootNamespace.Contains("aas/3/0") || rootName.Contains("aasenv3"))
                        return "3.0";
                    else if (rootNamespace.Contains("aas/2/0") || rootName.Contains("aasenv"))
                        return "2.0";
                    else if (rootNamespace.Contains("aas/1/0") || rootName.Contains("aasenv"))
                        return "1.0";
                }

                // Check for version-specific elements
                var aas3Nodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");
                var aas2Nodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");
                var aas1Nodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");

                if (aas3Nodes != null && aas3Nodes.Count > 0)
                    return "3.0";
                else if (aas2Nodes != null && aas2Nodes.Count > 0)
                    return "2.0";
                else if (aas1Nodes != null && aas1Nodes.Count > 0)
                    return "1.0";

                return "UNKNOWN";
            }
            catch
            {
                return "UNKNOWN";
            }
        }

        private System.Xml.XmlNamespaceManager CreateNamespaceManager(System.Xml.XmlDocument doc)
        {
            var nsManager = new System.Xml.XmlNamespaceManager(doc.NameTable);
            
            // Add standard namespaces
            nsManager.AddNamespace("xsi", "http://www.w3.org/2001/XMLSchema-instance");
            nsManager.AddNamespace("xs", "http://www.w3.org/2001/XMLSchema");
            
            // Dynamically detect AAS namespaces from the document
            DetectAndAddAasNamespaces(doc, nsManager);
            
            return nsManager;
        }
        
        private void DetectAndAddAasNamespaces(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager)
        {
            try
            {
                // Get all namespace declarations from the document
                var namespaceNodes = doc.SelectNodes("//namespace::*");
                if (namespaceNodes != null)
                {
                    foreach (System.Xml.XmlNode nsNode in namespaceNodes)
                    {
                        var namespaceUri = nsNode.Value;
                        var prefix = nsNode.LocalName;
                        
                        // Check if this is an AAS namespace
                        if (IsAasNamespace(namespaceUri))
                        {
                            // Use a standardized prefix for AAS namespaces
                            var aasPrefix = GetAasPrefix(namespaceUri);
                            nsManager.AddNamespace(aasPrefix, namespaceUri);
                            Console.WriteLine($"Detected AAS namespace: {aasPrefix} -> {namespaceUri}");
                        }
                    }
                }
                
                // Fallback: Add common AAS namespaces if not detected
                AddCommonAasNamespaces(nsManager);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Error detecting namespaces: {ex.Message}");
                // Fallback to common namespaces
                AddCommonAasNamespaces(nsManager);
            }
        }
        
        private bool IsAasNamespace(string namespaceUri)
        {
            if (string.IsNullOrEmpty(namespaceUri))
                return false;
                
            // Check for AAS namespace patterns
            return namespaceUri.Contains("admin-shell.io/aas") ||
                   namespaceUri.Contains("admin-shell.io/IEC61360") ||
                   namespaceUri.StartsWith("http://www.admin-shell.io/") ||
                   namespaceUri.StartsWith("https://www.admin-shell.io/");
        }
        
        private string GetAasPrefix(string namespaceUri)
        {
            // Extract version from namespace URI
            if (namespaceUri.Contains("/aas/1/"))
                return "aas1";
            else if (namespaceUri.Contains("/aas/2/"))
                return "aas2";
            else if (namespaceUri.Contains("/aas/3/"))
                return "aas3";
            else if (namespaceUri.Contains("/IEC61360/"))
                return "iec";
            else
                return "aas"; // Generic AAS prefix
        }
        
        private void AddCommonAasNamespaces(System.Xml.XmlNamespaceManager nsManager)
        {
            // Add common AAS namespaces as fallback
            var commonNamespaces = new Dictionary<string, string>
            {
                {"aas1", "http://www.admin-shell.io/aas/1/0"},
                {"aas2", "http://www.admin-shell.io/aas/2/0"},
                {"aas3", "http://www.admin-shell.io/aas/3/0"},
                {"aas", "http://www.admin-shell.io/aas/2/0"}, // Default to AAS 2.0
                {"iec", "http://www.admin-shell.io/IEC61360/2/0"}
            };
            
            foreach (var ns in commonNamespaces)
            {
                try
                {
                    nsManager.AddNamespace(ns.Key, ns.Value);
                }
                catch
                {
                    // Ignore if already exists
                }
            }
        }

        private void ExtractAas10Data(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager, 
            List<object> assets, List<object> submodels, string sourceFile)
        {
            // Use a HashSet to track processed IDs to avoid duplicates
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            // Try multiple prefixes for AAS 1.0
            var prefixes = new[] { "aas", "ns0" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var assetId = GetXmlElementTextWithPrefixes(aasNode, "identification");
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementTextWithPrefixes(aasNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(aasNode),
                                kind = GetXmlElementTextWithPrefixes(aasNode, "category"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            assets.Add(asset);
                            processedAssetIds.Add(assetId);
                            Console.WriteLine($"Found AAS 1.0 Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }

                // Extract Assets
                var assetNodes = doc.SelectNodes($"//{prefix}:asset", nsManager);
                if (assetNodes != null)
                {
                    foreach (System.Xml.XmlNode assetNode in assetNodes)
                    {
                        var assetId = GetXmlElementTextWithPrefixes(assetNode, "identification");
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementTextWithPrefixes(assetNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(assetNode),
                                kind = GetXmlElementTextWithPrefixes(assetNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            assets.Add(asset);
                            processedAssetIds.Add(assetId);
                            Console.WriteLine($"Found AAS 1.0 Asset: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }

                // Extract Submodels
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelId = GetXmlElementTextWithPrefixes(submodelNode, "identification");
                        if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                        {
                            var submodelData = new
                            {
                                id = submodelId,
                                idShort = GetXmlElementTextWithPrefixes(submodelNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(submodelNode),
                                kind = GetXmlElementTextWithPrefixes(submodelNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            submodels.Add(submodelData);
                            processedSubmodelIds.Add(submodelId);
                            Console.WriteLine($"Found AAS 1.0 Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                        }
                    }
                }
            }
        }

        private void ExtractAas30Data(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager,
            List<object> assets, List<object> submodels, string sourceFile)
        {
            // Try multiple prefixes for AAS 3.0
            var prefixes = new[] { "aas3", "ns1" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells (AAS 3.0)
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var asset = new
                        {
                            id = GetXmlElementTextWithPrefixes(aasNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(aasNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(aasNode),
                            kind = GetXmlElementTextWithPrefixes(aasNode, "kind"),
                            source = sourceFile,
                            format = "XML_AAS_3_0"
                        };
                        assets.Add(asset);
                        Console.WriteLine($"Found AAS 3.0 Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                    }
                }

                // Extract Submodels (AAS 3.0)
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelData = new
                        {
                            id = GetXmlElementTextWithPrefixes(submodelNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(submodelNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(submodelNode),
                            kind = GetXmlElementTextWithPrefixes(submodelNode, "kind"),
                            source = sourceFile,
                            format = "XML_AAS_3_0"
                        };
                        submodels.Add(submodelData);
                        Console.WriteLine($"Found AAS 3.0 Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                    }
                }
            }
        }

        private void ExtractGenericAasData(System.Xml.XmlDocument doc, List<object> assets, List<object> submodels, string sourceFile)
        {
            Console.WriteLine("Extracting generic AAS data (version-agnostic)...");
            
            try
            {
                // Find all asset administration shells
                var aasNodes = doc.SelectNodes("//*[local-name()='assetAdministrationShell']");
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var asset = new
                        {
                            id = GetXmlElementTextWithPrefixes(aasNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(aasNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(aasNode),
                            kind = GetXmlElementTextWithPrefixes(aasNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        
                        if (!string.IsNullOrEmpty(asset.id) || !string.IsNullOrEmpty(asset.idShort))
                        {
                            assets.Add(asset);
                            Console.WriteLine($"Found Generic Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }
                
                // Find all submodels
                var submodelNodes = doc.SelectNodes("//*[local-name()='submodel']");
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelData = new
                        {
                            id = GetXmlElementTextWithPrefixes(submodelNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(submodelNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(submodelNode),
                            kind = GetXmlElementTextWithPrefixes(submodelNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        
                        if (!string.IsNullOrEmpty(submodelData.id) || !string.IsNullOrEmpty(submodelData.idShort))
                        {
                            submodels.Add(submodelData);
                            Console.WriteLine($"Found Generic Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                        }
                    }
                }
                
                // Find all assets (if any)
                var assetNodes = doc.SelectNodes("//*[local-name()='asset']");
                if (assetNodes != null)
                {
                    foreach (System.Xml.XmlNode assetNode in assetNodes)
                    {
                        var asset = new
                        {
                            id = GetXmlElementTextWithPrefixes(assetNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(assetNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(assetNode),
                            kind = GetXmlElementTextWithPrefixes(assetNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        
                        if (!string.IsNullOrEmpty(asset.id) || !string.IsNullOrEmpty(asset.idShort))
                        {
                            assets.Add(asset);
                            Console.WriteLine($"Found Generic Asset: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error extracting generic AAS data: {ex.Message}");
            }
        }

        private void ExtractAas20Data(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager,
            List<object> assets, List<object> submodels, string sourceFile)
        {
            Console.WriteLine("Extracting AAS 2.0 data...");
            
            // Use a HashSet to track processed IDs to avoid duplicates
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            // Try multiple prefixes for AAS 2.0
            var prefixes = new[] { "aas", "ns0" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells (AAS 2.0)
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var identificationNode = aasNode.SelectSingleNode($"{prefix}:identification", nsManager);
                        var assetId = "";
                        if (identificationNode != null)
                        {
                            assetId = identificationNode.InnerText?.Trim();
                        }
                        
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementTextWithPrefixes(aasNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(aasNode),
                                kind = GetXmlElementTextWithPrefixes(aasNode, "category"),
                                source = sourceFile,
                                format = "XML_AAS_2_0"
                            };
                            assets.Add(asset);
                            processedAssetIds.Add(assetId);
                            Console.WriteLine($"Found AAS 2.0 Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }

                // Extract Assets (AAS 2.0)
                var assetNodes = doc.SelectNodes($"//{prefix}:asset", nsManager);
                if (assetNodes != null)
                {
                    foreach (System.Xml.XmlNode assetNode in assetNodes)
                    {
                        var identificationNode = assetNode.SelectSingleNode($"{prefix}:identification", nsManager);
                        var assetId = "";
                        if (identificationNode != null)
                        {
                            assetId = identificationNode.InnerText?.Trim();
                        }
                        
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementTextWithPrefixes(assetNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(assetNode),
                                kind = GetXmlElementTextWithPrefixes(assetNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_2_0"
                            };
                            assets.Add(asset);
                            processedAssetIds.Add(assetId);
                            Console.WriteLine($"Found AAS 2.0 Asset: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }

                // Extract Submodels (AAS 2.0)
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        // Get ID from identification element - try multiple approaches
                        var submodelId = "";
                        
                        // Try with namespace manager first
                        var identificationNode = submodelNode.SelectSingleNode("aas:identification", nsManager);
                        if (identificationNode != null)
                        {
                            submodelId = identificationNode.InnerText?.Trim() ?? "";
                        }
                        
                        // If not found, try without namespace
                        if (string.IsNullOrEmpty(submodelId))
                        {
                            identificationNode = submodelNode.SelectSingleNode("identification");
                            if (identificationNode != null)
                            {
                                submodelId = identificationNode.InnerText?.Trim() ?? "";
                            }
                        }
                        
                        // If still not found, try with local-name
                        if (string.IsNullOrEmpty(submodelId))
                        {
                            identificationNode = submodelNode.SelectSingleNode("*[local-name()='identification']");
                            if (identificationNode != null)
                            {
                                submodelId = identificationNode.InnerText?.Trim() ?? "";
                            }
                        }
                        
                        Console.WriteLine($"Submodel ID extracted: '{submodelId}'");
                        
                        if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                        {
                            processedSubmodelIds.Add(submodelId);
                            
                            var submodel = new
                            {
                                id = submodelId,
                                idShort = GetXmlElementText(submodelNode, "idShort"),
                                description = GetXmlDescription(submodelNode),
                                kind = GetXmlElementText(submodelNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_2_0"
                            };
                            submodels.Add(submodel);
                            Console.WriteLine($"Added submodel: {submodel.idShort} ({submodel.id})");
                        }
                    }
                }
            }
        }

        private string GetXmlAttribute(System.Xml.XmlNode node, string attributeName)
        {
            var attr = node.Attributes?[attributeName];
            return attr?.Value ?? "";
        }

        private string GetXmlElementText(System.Xml.XmlNode node, string elementName)
        {
            try
            {
                var element = node.SelectSingleNode(elementName, CreateNamespaceManager(node.OwnerDocument));
                if (element != null)
                {
                    // For identification elements, get the text content
                    if (elementName == "aas:identification")
                    {
                        return element.InnerText ?? "";
                    }
                    return element.InnerText ?? "";
                }
            }
            catch
            {
                // If namespace query fails, try without namespace
                try
                {
                    var elementNameWithoutNs = elementName.Replace("aas:", "");
                    var element = node.SelectSingleNode(elementNameWithoutNs);
                    if (element != null)
                    {
                        return element.InnerText ?? "";
                    }
                }
                catch
                {
                    // Ignore errors
                }
            }
            return "";
        }

        private string GetJsonProperty(JsonElement element, string propertyName)
        {
            if (element.TryGetProperty(propertyName, out var property))
            {
                return property.GetString() ?? "";
            }
            return "";
        }

        private string GetDescription(JsonElement element)
        {
            if (element.TryGetProperty("description", out var description))
            {
                if (description.ValueKind == JsonValueKind.String)
                {
                    return description.GetString() ?? "";
                }
                else if (description.ValueKind == JsonValueKind.Object)
                {
                    // Try to get English description
                    if (description.TryGetProperty("en", out var enDesc))
                    {
                        return enDesc.GetString() ?? "";
                    }
                    // Get first available description
                    foreach (var prop in description.EnumerateObject())
                    {
                        return prop.Value.GetString() ?? "";
                    }
                }
            }
            return "";
        }

        private string GetXmlDescription(System.Xml.XmlNode node)
        {
            try
            {
                var descriptionNode = node.SelectSingleNode("aas:description", CreateNamespaceManager(node.OwnerDocument));
                if (descriptionNode != null)
                {
                    var langStringNode = descriptionNode.SelectSingleNode("aas:langString[@lang='EN']", CreateNamespaceManager(node.OwnerDocument));
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("aas:langString", CreateNamespaceManager(node.OwnerDocument));
                    return anyLangString?.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors and return empty string
            }
            return "";
        }

        private string GetXmlElementTextWithPrefixes(System.Xml.XmlNode node, string elementName)
        {
            // Get all AAS prefixes from the namespace manager
            var aasPrefixes = GetAasPrefixes(node.OwnerDocument);
            
            // Try each AAS prefix
            foreach (var prefix in aasPrefixes)
            {
                var result = GetXmlElementText(node, prefix + ":" + elementName);
                if (!string.IsNullOrEmpty(result))
                {
                    Console.WriteLine($"Found element '{elementName}' with prefix '{prefix}': {result}");
                    return result;
                }
            }
            
            // Try without prefix (local name)
            var localResult = GetXmlElementText(node, elementName);
            if (!string.IsNullOrEmpty(localResult))
            {
                Console.WriteLine($"Found element '{elementName}' without prefix: {localResult}");
                return localResult;
            }
            
            // Try with local-name() XPath function (namespace-agnostic)
            var genericResult = GetGenericElementText(node, elementName);
            if (!string.IsNullOrEmpty(genericResult))
            {
                Console.WriteLine($"Found element '{elementName}' using local-name(): {genericResult}");
                return genericResult;
            }
            
            return "";
        }
        
        private List<string> GetAasPrefixes(System.Xml.XmlDocument doc)
        {
            var prefixes = new List<string>();
            
            try
            {
                var nsManager = CreateNamespaceManager(doc);
                
                // Get all namespace prefixes
                var namespaces = new string[] { "aas", "aas1", "aas2", "aas3", "iec", "ns0", "ns1", "ns2" };
                
                foreach (var prefix in namespaces)
                {
                    try
                    {
                        var uri = nsManager.LookupNamespace(prefix);
                        if (!string.IsNullOrEmpty(uri) && IsAasNamespace(uri))
                        {
                            prefixes.Add(prefix);
                        }
                    }
                    catch
                    {
                        // Ignore missing prefixes
                    }
                }
            }
            catch
            {
                // Fallback to common prefixes
                prefixes.AddRange(new string[] { "aas", "aas1", "aas2", "aas3", "iec" });
            }
            
            return prefixes;
        }

        private string GetXmlDescriptionWithPrefixes(System.Xml.XmlNode node)
        {
            // Try with aas: prefix first
            try
            {
                var descriptionNode = node.SelectSingleNode("aas:description", CreateNamespaceManager(node.OwnerDocument));
                if (descriptionNode != null)
                {
                    var langStringNode = descriptionNode.SelectSingleNode("aas:langString[@lang='EN']", CreateNamespaceManager(node.OwnerDocument));
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("aas:langString", CreateNamespaceManager(node.OwnerDocument));
                    return anyLangString?.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors and continue
            }
            
            // Try with ns0: prefix
            try
            {
                var descriptionNode = node.SelectSingleNode("ns0:description", CreateNamespaceManager(node.OwnerDocument));
                if (descriptionNode != null)
                {
                    var langStringNode = descriptionNode.SelectSingleNode("ns0:langString[@lang='EN']", CreateNamespaceManager(node.OwnerDocument));
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("ns0:langString", CreateNamespaceManager(node.OwnerDocument));
                    return anyLangString?.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors and continue
            }
            
            return "";
        }

        private string GetGenericElementText(System.Xml.XmlNode node, string elementName)
        {
            try
            {
                // Try to find element by local name (ignoring namespace)
                var element = node.SelectSingleNode($"*[local-name()='{elementName}']");
                if (element != null)
                {
                    return element.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors
            }
            return null;
        }

        private string GetGenericDescription(System.Xml.XmlNode node)
        {
            try
            {
                // Try to find description element
                var descriptionNode = node.SelectSingleNode("*[local-name()='description']");
                if (descriptionNode != null)
                {
                    // Try to find English langString
                    var langStringNode = descriptionNode.SelectSingleNode("*[local-name()='langString'][@lang='EN']");
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("*[local-name()='langString']");
                    if (anyLangString != null)
                    {
                        return anyLangString.InnerText ?? "";
                    }
                    
                    // Fallback to direct text content
                    return descriptionNode.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors
            }
            return "";
        }

        /// <summary>
        /// Generate an AASX file from JSON data
        /// </summary>
        /// <param name="jsonData">JSON string containing AAS data</param>
        /// <param name="outputPath">Path where the AASX file should be saved</param>
        /// <param name="embeddedFiles">Dictionary of embedded file paths</param>
        /// <returns>Success status and file path</returns>
        public string GenerateAasxFile(string jsonData, string outputPath, Dictionary<string, string> embeddedFiles = null)
        {
            try
            {
                // Parse JSON data
                var aasData = JsonSerializer.Deserialize<JsonElement>(jsonData);
                
                // Create AASX package using ZIP file operations (simpler approach)
                using (var zip = System.IO.Compression.ZipFile.Open(outputPath, System.IO.Compression.ZipArchiveMode.Create))
                {
                    // Add AASX origin file
                    var originEntry = zip.CreateEntry("aasx/aasx-origin");
                    using (var writer = new StreamWriter(originEntry.Open()))
                    {
                        writer.Write("Intentionally empty.");
                    }
                    
                    // Add content types file
                    var contentTypesEntry = zip.CreateEntry("[Content_Types].xml");
                    using (var writer = new StreamWriter(contentTypesEntry.Open()))
                    {
                        writer.Write(@"<?xml version=""1.0"" encoding=""UTF-8""?>
<Types xmlns=""http://schemas.openxmlformats.org/package/2006/content-types"">
    <Default Extension=""rels"" ContentType=""application/vnd.openxmlformats-package.relationships+xml""/>
    <Default Extension=""xml"" ContentType=""text/xml""/>
    <Default Extension=""JPG"" ContentType=""image/jpeg""/>
    <Default Extension=""PDF"" ContentType=""application/pdf""/>
    <Override PartName=""/aasx/aasx-origin"" ContentType=""text/plain""/>
</Types>");
                    }
                    
                    // Add relationships file
                    var relsEntry = zip.CreateEntry("_rels/.rels");
                    using (var writer = new StreamWriter(relsEntry.Open()))
                    {
                        writer.Write(@"<?xml version=""1.0"" encoding=""UTF-8""?>
<Relationships xmlns=""http://schemas.openxmlformats.org/package/2006/relationships"">
    <Relationship Id=""r1"" Type=""http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"" Target=""docProps/core.xml""/>
</Relationships>");
                    }
                    
                    // Add AAS XML content with proper naming
                    if (aasData.TryGetProperty("assets", out var assetsArray))
                    {
                        var xmlContent = GenerateAasXml(aasData);
                        
                        // Use a proper AAS XML filename based on the first asset
                        string aasXmlFileName = "aas_content.aas.xml";
                        if (assetsArray.GetArrayLength() > 0)
                        {
                            var firstAsset = assetsArray[0];
                            if (firstAsset.TryGetProperty("idShort", out var idShortElement))
                            {
                                var idShort = idShortElement.GetString();
                                if (!string.IsNullOrEmpty(idShort))
                                {
                                    aasXmlFileName = $"{idShort.ToLowerInvariant()}_aas.aas.xml";
                                }
                            }
                        }
                        
                        var xmlEntry = zip.CreateEntry($"aasx/{aasXmlFileName}");
                        using (var writer = new StreamWriter(xmlEntry.Open()))
                        {
                            writer.Write(xmlContent);
                        }
                        
                        // Add AASX origin relationships
                        var originRelsEntry = zip.CreateEntry("aasx/_rels/aasx-origin.rels");
                        using (var writer = new StreamWriter(originRelsEntry.Open()))
                        {
                            writer.Write($@"<?xml version=""1.0"" encoding=""utf-8""?>
<Relationships xmlns=""http://schemas.openxmlformats.org/package/2006/relationships"">
    <Relationship Type=""http://www.admin-shell.io/aasx/relationships/aas-spec"" Target=""/aasx/{aasXmlFileName}"" Id=""R1"" />
</Relationships>");
                        }
                        
                        // Add relationship file for the AAS XML
                        var aasXmlRelsEntry = zip.CreateEntry($"aasx/_rels/{aasXmlFileName}.rels");
                        using (var writer = new StreamWriter(aasXmlRelsEntry.Open()))
                        {
                            writer.Write(@"<?xml version=""1.0"" encoding=""utf-8""?>
<Relationships xmlns=""http://schemas.openxmlformats.org/package/2006/relationships"">
</Relationships>");
                        }
                    }
                    
                    // Add embedded files
                    if (embeddedFiles != null)
                    {
                        foreach (var fileEntry in embeddedFiles)
                        {
                            var filePath = fileEntry.Value;
                            var aasxPath = fileEntry.Key;
                            
                            if (File.Exists(filePath))
                            {
                                var entry = zip.CreateEntry(aasxPath);
                                using (var entryStream = entry.Open())
                                using (var fileStream = File.OpenRead(filePath))
                                {
                                    fileStream.CopyTo(entryStream);
                                }
                            }
                        }
                    }
                }
                
                var result = new
                {
                    success = true,
                    output_path = outputPath,
                    processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                    embedded_files_count = embeddedFiles?.Count ?? 0
                };
                
                return JsonSerializer.Serialize(result, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
            catch (Exception ex)
            {
                var error = new
                {
                    success = false,
                    error = ex.Message,
                    output_path = outputPath,
                    processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
                };
                
                return JsonSerializer.Serialize(error, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
        }
        
        /// <summary>
        /// Generate AAS XML content from JSON data
        /// </summary>
        private string GenerateAasXml(JsonElement aasData)
        {
            var xml = @"<?xml version=""1.0"" encoding=""UTF-8""?>
<aasenv xmlns=""http://www.admin-shell.io/aas/3/0"">
    <assetAdministrationShells>";
            
            if (aasData.TryGetProperty("assets", out var assetsArray))
            {
                foreach (var asset in assetsArray.EnumerateArray())
                {
                    xml += @"
        <assetAdministrationShell>";
                    
                    if (asset.TryGetProperty("idShort", out var idShortElement))
                        xml += $@"
            <idShort>{idShortElement.GetString()}</idShort>";
                    
                    if (asset.TryGetProperty("id", out var idElement))
                        xml += $@"
            <identification idType=""IRI"">{idElement.GetString()}</identification>";
                    
                    if (asset.TryGetProperty("kind", out var kindElement))
                        xml += $@"
            <category>{kindElement.GetString()}</category>";
                    
                    xml += @"
        </assetAdministrationShell>";
                }
            }
            
            xml += @"
    </assetAdministrationShells>
</aasenv>";
            
            return xml;
        }

        /// <summary>
        /// Extract all namespaces from XML document
        /// </summary>
        private void ExtractAllNamespaces(System.Xml.XmlDocument doc, Dictionary<string, string> namespaces)
        {
            try
            {
                var namespaceNodes = doc.SelectNodes("//namespace::*");
                if (namespaceNodes != null)
                {
                    foreach (System.Xml.XmlNode nsNode in namespaceNodes)
                    {
                        var namespaceUri = nsNode.Value;
                        var prefix = nsNode.LocalName;
                        
                        if (!string.IsNullOrEmpty(namespaceUri) && !string.IsNullOrEmpty(prefix))
                        {
                            namespaces[prefix] = namespaceUri;
                            Console.WriteLine($"Detected namespace: {prefix} -> {namespaceUri}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Error extracting namespaces: {ex.Message}");
            }
        }

        /// <summary>
        /// Enhanced AAS 1.0 data extraction with relationship tracking
        /// </summary>
        private void ExtractAas10DataEnhanced(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager,
            List<object> assets, List<object> submodels, string sourceFile, 
            List<object> assetSubmodelRelationships, List<object> fileRelationships)
        {
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            var prefixes = new[] { "aas", "ns0" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells with relationship tracking
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var assetId = GetXmlAttribute(aasNode, "id");
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            processedAssetIds.Add(assetId);
                            
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementText(aasNode, "idShort"),
                                description = GetXmlDescription(aasNode),
                                kind = GetXmlElementText(aasNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            assets.Add(asset);
                            
                            // Track submodel relationships
                            var submodelRefs = aasNode.SelectNodes($"{prefix}:submodels/{prefix}:submodel", nsManager);
                            if (submodelRefs != null)
                            {
                                foreach (System.Xml.XmlNode submodelRef in submodelRefs)
                                {
                                    var submodelId = GetXmlAttribute(submodelRef, "id");
                                    if (!string.IsNullOrEmpty(submodelId))
                                    {
                                        assetSubmodelRelationships.Add(new
                                        {
                                            asset_id = assetId,
                                            submodel_id = submodelId,
                                            relationship_type = "submodel_reference",
                                            source = sourceFile
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Extract Submodels with file relationship tracking
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelId = GetXmlAttribute(submodelNode, "id");
                        if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                        {
                            processedSubmodelIds.Add(submodelId);
                            
                            var submodel = new
                            {
                                id = submodelId,
                                idShort = GetXmlElementText(submodelNode, "idShort"),
                                description = GetXmlDescription(submodelNode),
                                kind = GetXmlElementText(submodelNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            submodels.Add(submodel);
                            
                            // Track file relationships
                            ExtractFileRelationshipsFromSubmodel(submodelNode, submodelId, fileRelationships, sourceFile, prefix, nsManager);
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Enhanced AAS 2.0 data extraction with relationship tracking
        /// </summary>
        private void ExtractAas20DataEnhanced(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager,
            List<object> assets, List<object> submodels, string sourceFile,
            List<object> assetSubmodelRelationships, List<object> fileRelationships)
        {
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            Console.WriteLine($"ExtractAas20DataEnhanced: Processing file {sourceFile}");
            
            // Try multiple approaches to extract assets
            var assetXPaths = new[] {
                "//aas:asset",
                "//asset", 
                "//*[local-name()='asset']",
                "//aas:assets/aas:asset",
                "//assets/asset"
            };
            
            foreach (var xpath in assetXPaths)
            {
                var assetNodes = doc.SelectNodes(xpath, nsManager);
                if (assetNodes != null && assetNodes.Count > 0)
                {
                    Console.WriteLine($"Found {assetNodes.Count} assets with XPath: {xpath}");
                    
                    foreach (System.Xml.XmlNode assetNode in assetNodes)
                    {
                        // Extract basic asset information
                        var assetId = "";
                        var assetIdShort = "";
                        var assetCategory = "";
                        var assetKind = "";
                        
                        // Get idShort
                        var idShortNode = assetNode.SelectSingleNode("aas:idShort", nsManager) ?? 
                                        assetNode.SelectSingleNode("idShort", nsManager) ??
                                        assetNode.SelectSingleNode("*[local-name()='idShort']", nsManager);
                        if (idShortNode != null)
                        {
                            assetIdShort = idShortNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Get identification
                        var identificationNode = assetNode.SelectSingleNode("aas:identification", nsManager) ?? 
                                               assetNode.SelectSingleNode("identification", nsManager) ??
                                               assetNode.SelectSingleNode("*[local-name()='identification']", nsManager);
                        if (identificationNode != null)
                        {
                            assetId = identificationNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Get category
                        var categoryNode = assetNode.SelectSingleNode("aas:category", nsManager) ?? 
                                         assetNode.SelectSingleNode("category", nsManager) ??
                                         assetNode.SelectSingleNode("*[local-name()='category']", nsManager);
                        if (categoryNode != null)
                        {
                            assetCategory = categoryNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Get kind
                        var kindNode = assetNode.SelectSingleNode("aas:kind", nsManager) ?? 
                                     assetNode.SelectSingleNode("kind", nsManager) ??
                                     assetNode.SelectSingleNode("*[local-name()='kind']", nsManager);
                        if (kindNode != null)
                        {
                            assetKind = kindNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Use idShort as fallback ID if identification is empty
                        if (string.IsNullOrEmpty(assetId) && !string.IsNullOrEmpty(assetIdShort))
                        {
                            assetId = assetIdShort;
                        }
                        
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            processedAssetIds.Add(assetId);
                            
                            var assetData = new Dictionary<string, object>
                            {
                                ["id"] = assetId,
                                ["idShort"] = assetIdShort,
                                ["category"] = assetCategory,
                                ["kind"] = assetKind,
                                ["source_file"] = sourceFile
                            };
                            
                            assets.Add(assetData);
                            Console.WriteLine($"Added asset: {assetIdShort} ({assetId})");
                        }
                    }
                    break; // Found assets, no need to try other XPaths
                }
                else
                {
                    Console.WriteLine($"No assets found with XPath: {xpath}");
                }
            }
            
            // Try multiple approaches to extract submodels
            var submodelXPaths = new[] {
                "//aas:submodel",
                "//submodel",
                "//*[local-name()='submodel']",
                "//aas:submodels/aas:submodel",
                "//submodels/submodel"
            };
            
            foreach (var xpath in submodelXPaths)
            {
                var submodelNodes = doc.SelectNodes(xpath, nsManager);
                if (submodelNodes != null && submodelNodes.Count > 0)
                {
                    Console.WriteLine($"Found {submodelNodes.Count} submodels with XPath: {xpath}");
                    
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        // Extract basic submodel information
                        var submodelId = "";
                        var submodelIdShort = "";
                        var submodelCategory = "";
                        var submodelKind = "";
                        
                        // Get idShort
                        var idShortNode = submodelNode.SelectSingleNode("aas:idShort", nsManager) ?? 
                                        submodelNode.SelectSingleNode("idShort", nsManager) ??
                                        submodelNode.SelectSingleNode("*[local-name()='idShort']", nsManager);
                        if (idShortNode != null)
                        {
                            submodelIdShort = idShortNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Get identification
                        var identificationNode = submodelNode.SelectSingleNode("aas:identification", nsManager) ?? 
                                               submodelNode.SelectSingleNode("identification", nsManager) ??
                                               submodelNode.SelectSingleNode("*[local-name()='identification']", nsManager);
                        if (identificationNode != null)
                        {
                            submodelId = identificationNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Get category
                        var categoryNode = submodelNode.SelectSingleNode("aas:category", nsManager) ?? 
                                         submodelNode.SelectSingleNode("category", nsManager) ??
                                         submodelNode.SelectSingleNode("*[local-name()='category']", nsManager);
                        if (categoryNode != null)
                        {
                            submodelCategory = categoryNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Get kind
                        var kindNode = submodelNode.SelectSingleNode("aas:kind", nsManager) ?? 
                                     submodelNode.SelectSingleNode("kind", nsManager) ??
                                     submodelNode.SelectSingleNode("*[local-name()='kind']", nsManager);
                        if (kindNode != null)
                        {
                            submodelKind = kindNode.InnerText?.Trim() ?? "";
                        }
                        
                        // Use idShort as fallback ID if identification is empty
                        if (string.IsNullOrEmpty(submodelId) && !string.IsNullOrEmpty(submodelIdShort))
                        {
                            submodelId = submodelIdShort;
                        }
                        
                        if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                        {
                            processedSubmodelIds.Add(submodelId);
                            
                            var submodelData = new Dictionary<string, object>
                            {
                                ["id"] = submodelId,
                                ["idShort"] = submodelIdShort,
                                ["category"] = submodelCategory,
                                ["kind"] = submodelKind,
                                ["source_file"] = sourceFile
                            };
                            
                            submodels.Add(submodelData);
                            Console.WriteLine($"Added submodel: {submodelIdShort} ({submodelId})");
                        }
                    }
                    break; // Found submodels, no need to try other XPaths
                }
                else
                {
                    Console.WriteLine($"No submodels found with XPath: {xpath}");
                }
            }
            
            Console.WriteLine($"ExtractAas20DataEnhanced: Final count - Assets: {assets.Count}, Submodels: {submodels.Count}");
            
            // Extract Asset Administration Shells for relationship tracking
            Console.WriteLine("Extracting asset-submodel relationships...");
            var aasNodes = doc.SelectNodes("//*[local-name()='assetAdministrationShell']", nsManager);
            
            Console.WriteLine($"Found {aasNodes?.Count ?? 0} assetAdministrationShell nodes");
            
            if (aasNodes != null)
            {
                foreach (System.Xml.XmlNode aasNode in aasNodes)
                {
                    // Get AAS identification
                    var aasIdentificationNode = aasNode.SelectSingleNode("*[local-name()='identification']", nsManager);
                    var aasId = "";
                    if (aasIdentificationNode != null)
                    {
                        aasId = aasIdentificationNode.InnerText?.Trim() ?? "";
                        Console.WriteLine($"Found AAS with ID: {aasId}");
                    }
                    
                    // Track submodel relationships
                    var submodelRefs = aasNode.SelectNodes("*[local-name()='submodelRefs']/*[local-name()='submodelRef']", nsManager);
                    
                    Console.WriteLine($"Found {submodelRefs?.Count ?? 0} submodelRef nodes");
                    
                    if (submodelRefs != null)
                    {
                        foreach (System.Xml.XmlNode submodelRef in submodelRefs)
                        {
                            var submodelId = "";
                            
                            // Get submodel ID from keys
                            var keyNodes = submodelRef.SelectNodes("*[local-name()='keys']/*[local-name()='key']", nsManager);
                            
                            if (keyNodes != null && keyNodes.Count > 0)
                            {
                                var keyNode = keyNodes[0]; // Take first key
                                submodelId = keyNode.InnerText?.Trim() ?? "";
                                Console.WriteLine($"Found submodel reference: {submodelId}");
                            }
                            
                            if (!string.IsNullOrEmpty(submodelId) && !string.IsNullOrEmpty(aasId))
                            {
                                assetSubmodelRelationships.Add(new Dictionary<string, object>
                                {
                                    ["asset_id"] = aasId,
                                    ["submodel_id"] = submodelId,
                                    ["relationship_type"] = "submodel_reference",
                                    ["source_file"] = sourceFile
                                });
                                Console.WriteLine($"Added asset-submodel relationship: {aasId} -> {submodelId}");
                            }
                        }
                    }
                }
            }
            
            // Extract file relationships from AASX structure
            Console.WriteLine("Extracting file relationships...");
            var fileElements = doc.SelectNodes("//*[local-name()='file']", nsManager);
            
            Console.WriteLine($"Found {fileElements?.Count ?? 0} file elements");
            
            if (fileElements != null)
            {
                foreach (System.Xml.XmlNode fileElement in fileElements)
                {
                    var filePath = "";
                    var fileId = "";
                    var fileIdShort = "";
                    
                    // Get file path
                    var valueNode = fileElement.SelectSingleNode("*[local-name()='value']", nsManager);
                    if (valueNode != null)
                    {
                        filePath = valueNode.InnerText?.Trim() ?? "";
                        Console.WriteLine($"Found file path: {filePath}");
                    }
                    
                    // Get file idShort
                    var idShortNode = fileElement.SelectSingleNode("*[local-name()='idShort']", nsManager);
                    if (idShortNode != null)
                    {
                        fileIdShort = idShortNode.InnerText?.Trim() ?? "";
                        Console.WriteLine($"Found file idShort: {fileIdShort}");
                    }
                    
                    // Get file ID from parent submodel (traverse up the hierarchy)
                    var currentNode = fileElement.ParentNode;
                    while (currentNode != null && string.IsNullOrEmpty(fileId))
                    {
                        var submodelIdNode = currentNode.SelectSingleNode("*[local-name()='identification']", nsManager);
                        if (submodelIdNode != null)
                        {
                            fileId = submodelIdNode.InnerText?.Trim() ?? "";
                            Console.WriteLine($"Found file ID from parent: {fileId}");
                            break;
                        }
                        currentNode = currentNode.ParentNode;
                    }
                    
                    if (!string.IsNullOrEmpty(filePath))
                    {
                        fileRelationships.Add(new Dictionary<string, object>
                        {
                            ["element_id"] = fileId,
                            ["element_idShort"] = fileIdShort,
                            ["file_path"] = filePath,
                            ["relationship_type"] = "file_reference",
                            ["source_file"] = sourceFile
                        });
                        Console.WriteLine($"Added file relationship: {fileIdShort} ({fileId}) -> {filePath}");
                    }
                }
            }
            
            Console.WriteLine($"Final relationship counts - Asset-Submodel: {assetSubmodelRelationships.Count}, File: {fileRelationships.Count}");
        }

        /// <summary>
        /// Enhanced AAS 3.0 data extraction with relationship tracking
        /// </summary>
        private void ExtractAas30DataEnhanced(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager,
            List<object> assets, List<object> submodels, string sourceFile,
            List<object> assetSubmodelRelationships, List<object> fileRelationships)
        {
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            var prefixes = new[] { "aas", "aas3", "ns0" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells with relationship tracking
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var assetId = GetXmlAttribute(aasNode, "id");
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            processedAssetIds.Add(assetId);
                            
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementText(aasNode, "idShort"),
                                description = GetXmlDescription(aasNode),
                                kind = GetXmlElementText(aasNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_3_0"
                            };
                            assets.Add(asset);
                            
                            // Track submodel relationships
                            var submodelRefs = aasNode.SelectNodes($"{prefix}:submodels/{prefix}:submodelRef", nsManager);
                            if (submodelRefs != null)
                            {
                                foreach (System.Xml.XmlNode submodelRef in submodelRefs)
                                {
                                    var submodelId = GetXmlAttribute(submodelRef, "id");
                                    if (!string.IsNullOrEmpty(submodelId))
                                    {
                                        assetSubmodelRelationships.Add(new
                                        {
                                            asset_id = assetId,
                                            submodel_id = submodelId,
                                            relationship_type = "submodel_reference",
                                            source = sourceFile
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Extract Submodels with file relationship tracking
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelId = GetXmlAttribute(submodelNode, "id");
                        if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                        {
                            processedSubmodelIds.Add(submodelId);
                            
                            var submodel = new
                            {
                                id = submodelId,
                                idShort = GetXmlElementText(submodelNode, "idShort"),
                                description = GetXmlDescription(submodelNode),
                                kind = GetXmlElementText(submodelNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_3_0"
                            };
                            submodels.Add(submodel);
                            
                            // Track file relationships
                            ExtractFileRelationshipsFromSubmodel(submodelNode, submodelId, fileRelationships, sourceFile, prefix, nsManager);
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Enhanced generic AAS data extraction with relationship tracking
        /// </summary>
        private void ExtractGenericAasDataEnhanced(System.Xml.XmlDocument doc, List<object> assets, List<object> submodels, 
            string sourceFile, List<object> assetSubmodelRelationships, List<object> fileRelationships)
        {
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            // Generic extraction without namespace prefixes
            var aasNodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");
            if (aasNodes != null)
            {
                foreach (System.Xml.XmlNode aasNode in aasNodes)
                {
                    var assetId = GetXmlAttribute(aasNode, "id");
                    if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                    {
                        processedAssetIds.Add(assetId);
                        
                        var asset = new
                        {
                            id = assetId,
                            idShort = GetGenericElementText(aasNode, "idShort"),
                            description = GetGenericDescription(aasNode),
                            kind = GetGenericElementText(aasNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        assets.Add(asset);
                        
                        // Track submodel relationships
                        var submodelRefs = aasNode.SelectNodes(".//*[contains(local-name(), 'submodel')]");
                        if (submodelRefs != null)
                        {
                            foreach (System.Xml.XmlNode submodelRef in submodelRefs)
                            {
                                var submodelId = GetXmlAttribute(submodelRef, "id");
                                if (!string.IsNullOrEmpty(submodelId))
                                {
                                    assetSubmodelRelationships.Add(new
                                    {
                                        asset_id = assetId,
                                        submodel_id = submodelId,
                                        relationship_type = "submodel_reference",
                                        source = sourceFile
                                    });
                                }
                            }
                        }
                    }
                }
            }
            
            var submodelNodes = doc.SelectNodes("//*[contains(local-name(), 'submodel')]");
            if (submodelNodes != null)
            {
                foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                {
                    var submodelId = GetXmlAttribute(submodelNode, "id");
                    if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                    {
                        processedSubmodelIds.Add(submodelId);
                        
                        var submodel = new
                        {
                            id = submodelId,
                            idShort = GetGenericElementText(submodelNode, "idShort"),
                            description = GetGenericDescription(submodelNode),
                            kind = GetGenericElementText(submodelNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        submodels.Add(submodel);
                        
                        // Track file relationships
                        ExtractFileRelationshipsFromSubmodelGeneric(submodelNode, submodelId, fileRelationships, sourceFile);
                    }
                }
            }
        }

        /// <summary>
        /// Extract file relationships from submodel elements
        /// </summary>
        private void ExtractFileRelationshipsFromSubmodel(System.Xml.XmlNode submodelNode, string submodelId, 
            List<object> fileRelationships, string sourceFile, string prefix, System.Xml.XmlNamespaceManager nsManager)
        {
            // Look for file references in submodel elements
            var fileElements = submodelNode.SelectNodes($".//{prefix}:file", nsManager);
            if (fileElements != null)
            {
                foreach (System.Xml.XmlNode fileElement in fileElements)
                {
                    var filePath = GetXmlElementText(fileElement, "value");
                    if (!string.IsNullOrEmpty(filePath))
                    {
                        fileRelationships.Add(new
                        {
                            file_path = filePath,
                            referenced_by = new[]
                            {
                                new
                                {
                                    element_type = "submodel",
                                    element_id = submodelId,
                                    relationship_type = "file_reference",
                                    source = sourceFile
                                }
                            }
                        });
                    }
                }
            }
            
            // Look for document references
            var documentElements = submodelNode.SelectNodes($".//{prefix}:document", nsManager);
            if (documentElements != null)
            {
                foreach (System.Xml.XmlNode documentElement in documentElements)
                {
                    var documentPath = GetXmlElementText(documentElement, "value");
                    if (!string.IsNullOrEmpty(documentPath))
                    {
                        fileRelationships.Add(new
                        {
                            file_path = documentPath,
                            referenced_by = new[]
                            {
                                new
                                {
                                    element_type = "submodel",
                                    element_id = submodelId,
                                    relationship_type = "document_reference",
                                    source = sourceFile
                                }
                            }
                        });
                    }
                }
            }
        }

        /// <summary>
        /// Extract file relationships from submodel elements (generic version)
        /// </summary>
        private void ExtractFileRelationshipsFromSubmodelGeneric(System.Xml.XmlNode submodelNode, string submodelId, 
            List<object> fileRelationships, string sourceFile)
        {
            // Look for file references in submodel elements (generic)
            var fileElements = submodelNode.SelectNodes(".//*[contains(local-name(), 'file')]");
            if (fileElements != null)
            {
                foreach (System.Xml.XmlNode fileElement in fileElements)
                {
                    var filePath = GetGenericElementText(fileElement, "value");
                    if (!string.IsNullOrEmpty(filePath))
                    {
                        fileRelationships.Add(new
                        {
                            file_path = filePath,
                            referenced_by = new[]
                            {
                                new
                                {
                                    element_type = "submodel",
                                    element_id = submodelId,
                                    relationship_type = "file_reference",
                                    source = sourceFile
                                }
                            }
                        });
                    }
                }
            }
            
            // Look for document references (generic)
            var documentElements = submodelNode.SelectNodes(".//*[contains(local-name(), 'document')]");
            if (documentElements != null)
            {
                foreach (System.Xml.XmlNode documentElement in documentElements)
                {
                    var documentPath = GetGenericElementText(documentElement, "value");
                    if (!string.IsNullOrEmpty(documentPath))
                    {
                        fileRelationships.Add(new
                        {
                            file_path = documentPath,
                            referenced_by = new[]
                            {
                                new
                                {
                                    element_type = "submodel",
                                    element_id = submodelId,
                                    relationship_type = "document_reference",
                                    source = sourceFile
                                }
                            }
                        });
                    }
                }
            }
        }

        /// <summary>
        /// Generate AASX file from structured JSON data (backward conversion)
        /// </summary>
        /// <param name="jsonData">JSON data containing structured AAS information</param>
        /// <param name="outputPath">Output path for the generated AASX file</param>
        /// <returns>Path to the generated AASX file</returns>
        public string GenerateAasxFileFromStructured(string jsonData, string jsonFilePath, string outputPath)
        {
            Console.WriteLine("Starting backward conversion from structured data...");
            
            try
            {
                var jsonDoc = JsonDocument.Parse(jsonData);
                var data = jsonDoc.RootElement;
                
                // Extract structured data
                var namespaces = ExtractNamespaces(data);
                var assets = ExtractAssets(data);
                var submodels = ExtractSubmodels(data);
                var assetSubmodelRelationships = ExtractAssetSubmodelRelationships(data);
                var fileRelationships = ExtractFileRelationships(data);
                var embeddedFiles = ExtractEmbeddedFiles(data);
                
                Console.WriteLine($"Extracted: {assets.Count} assets, {submodels.Count} submodels, {assetSubmodelRelationships.Count + fileRelationships.Count} relationships");
                
                // Generate AAS XML
                Console.WriteLine("Generating AAS XML from structured data...");
                var aasXml = GenerateAasXmlFromStructured(
                    data.GetProperty("aasVersion").GetString() ?? "3.0",
                    namespaces, assets, submodels, assetSubmodelRelationships, fileRelationships);
                Console.WriteLine("AAS XML generated successfully from structured data");
                
                // Create AASX package
                var aasxFilePath = CreateAasxPackageFromStructured(aasXml, embeddedFiles, jsonFilePath, outputPath);
                Console.WriteLine($"Successfully generated AASX file: {aasxFilePath}");
                
                return aasxFilePath;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in backward conversion: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Extract namespaces from JSON data
        /// </summary>
        private Dictionary<string, string> ExtractNamespaces(JsonElement data)
        {
            var namespaces = new Dictionary<string, string>();
            
            if (data.TryGetProperty("namespaces", out var nsElement))
            {
                foreach (var property in nsElement.EnumerateObject())
                {
                    namespaces[property.Name] = property.Value.GetString() ?? "";
                }
            }
            
            // Add default namespaces if not present
            if (!namespaces.ContainsKey("aas"))
                namespaces["aas"] = "http://www.admin-shell.io/aas/1/0";
            if (!namespaces.ContainsKey("IEC61360"))
                namespaces["IEC61360"] = "http://www.admin-shell.io/IEC61360/1/0";
            if (!namespaces.ContainsKey("xsi"))
                namespaces["xsi"] = "http://www.w3.org/2001/XMLSchema-instance";
            if (!namespaces.ContainsKey("xml"))
                namespaces["xml"] = "http://www.w3.org/XML/1998/namespace";
                
            return namespaces;
        }

        /// <summary>
        /// Extract assets from JSON data
        /// </summary>
        private List<Dictionary<string, object>> ExtractAssets(JsonElement data)
        {
            var assets = new List<Dictionary<string, object>>();
            
            if (data.TryGetProperty("assets", out var assetsElement))
            {
                foreach (var asset in assetsElement.EnumerateArray())
                {
                    var assetData = new Dictionary<string, object>();
                    foreach (var property in asset.EnumerateObject())
                    {
                        assetData[property.Name] = property.Value.ValueKind == JsonValueKind.String 
                            ? property.Value.GetString() ?? "" 
                            : property.Value.ToString();
                    }
                    assets.Add(assetData);
                }
            }
            
            return assets;
        }

        /// <summary>
        /// Extract submodels from JSON data
        /// </summary>
        private List<Dictionary<string, object>> ExtractSubmodels(JsonElement data)
        {
            var submodels = new List<Dictionary<string, object>>();
            
            if (data.TryGetProperty("submodels", out var submodelsElement))
            {
                foreach (var submodel in submodelsElement.EnumerateArray())
                {
                    var submodelData = new Dictionary<string, object>();
                    foreach (var property in submodel.EnumerateObject())
                    {
                        submodelData[property.Name] = property.Value.ValueKind == JsonValueKind.String 
                            ? property.Value.GetString() ?? "" 
                            : property.Value.ToString();
                    }
                    submodels.Add(submodelData);
                }
            }
            
            return submodels;
        }

        /// <summary>
        /// Extract asset-submodel relationships from JSON data
        /// </summary>
        private List<Dictionary<string, object>> ExtractAssetSubmodelRelationships(JsonElement data)
        {
            var relationships = new List<Dictionary<string, object>>();
            
            if (data.TryGetProperty("assetSubmodelRelationships", out var relsElement))
            {
                foreach (var rel in relsElement.EnumerateArray())
                {
                    var relData = new Dictionary<string, object>();
                    foreach (var property in rel.EnumerateObject())
                    {
                        relData[property.Name] = property.Value.ValueKind == JsonValueKind.String 
                            ? property.Value.GetString() ?? "" 
                            : property.Value.ToString();
                    }
                    relationships.Add(relData);
                }
            }
            
            return relationships;
        }

        /// <summary>
        /// Extract file relationships from JSON data
        /// </summary>
        private List<Dictionary<string, object>> ExtractFileRelationships(JsonElement data)
        {
            var relationships = new List<Dictionary<string, object>>();
            
            if (data.TryGetProperty("fileRelationships", out var relsElement))
            {
                foreach (var rel in relsElement.EnumerateArray())
                {
                    var relData = new Dictionary<string, object>();
                    foreach (var property in rel.EnumerateObject())
                    {
                        relData[property.Name] = property.Value.ValueKind == JsonValueKind.String 
                            ? property.Value.GetString() ?? "" 
                            : property.Value.ToString();
                    }
                    relationships.Add(relData);
                }
            }
            
            return relationships;
        }

        /// <summary>
        /// Extract embedded files from JSON data
        /// </summary>
        private Dictionary<string, Dictionary<string, object>> ExtractEmbeddedFiles(JsonElement data)
        {
            var embeddedFiles = new Dictionary<string, Dictionary<string, object>>();
            
            if (data.TryGetProperty("embeddedFiles", out var filesElement))
            {
                foreach (var file in filesElement.EnumerateObject())
                {
                    var fileData = new Dictionary<string, object>();
                    foreach (var property in file.Value.EnumerateObject())
                    {
                        fileData[property.Name] = property.Value.ValueKind == JsonValueKind.String 
                            ? property.Value.GetString() ?? "" 
                            : property.Value.ToString();
                    }
                    embeddedFiles[file.Name] = fileData;
                }
            }
            
            return embeddedFiles;
        }

        /// <summary>
        /// Generate AAS XML from structured data
        /// </summary>
        private string GenerateAasXmlFromStructured(string aasVersion, Dictionary<string, string> namespaces, 
            List<Dictionary<string, object>> assets, List<Dictionary<string, object>> submodels,
            List<Dictionary<string, object>> assetSubmodelRelationships, List<Dictionary<string, object>> fileRelationships)
        {
            Console.WriteLine("Generating AAS XML from structured data...");
            
            // Build namespace declarations
            var namespaceDeclarations = string.Join(" ", namespaces.Select(ns => $"xmlns:{ns.Key}=\"{ns.Value}\""));
            
            // Generate XML content
            var xml = new System.Text.StringBuilder();
            xml.AppendLine("<?xml version=\"1.0\"?>");
            xml.AppendLine($"<aas:aasenv {namespaceDeclarations} xsi:schemaLocation=\"http://www.admin-shell.io/aas/1/0 AAS.xsd http://www.admin-shell.io/IEC61360/1/0 IEC61360.xsd\">");
            
            // Generate Asset Administration Shells
            xml.AppendLine("  <aas:assetAdministrationShells>");
            foreach (var relationship in assetSubmodelRelationships)
            {
                var assetId = relationship.GetValueOrDefault("asset_id", "").ToString();
                if (!string.IsNullOrEmpty(assetId))
                {
                    xml.AppendLine("    <aas:assetAdministrationShell>");
                    xml.AppendLine("      <aas:idShort>ExampleMotor</aas:idShort>");
                    xml.AppendLine("      <aas:category>CONSTANT</aas:category>");
                    xml.AppendLine($"      <aas:identification idType=\"URI\">{assetId}</aas:identification>");
                    
                    // Add asset reference
                    var asset = assets.FirstOrDefault(a => a.GetValueOrDefault("id", "").ToString() == assetId);
                    if (asset != null)
                    {
                        xml.AppendLine("      <aas:assetRef>");
                        xml.AppendLine("        <aas:keys>");
                        xml.AppendLine($"          <aas:key type=\"Asset\" local=\"true\" idType=\"URI\">{asset.GetValueOrDefault("id", "")}</aas:key>");
                        xml.AppendLine("        </aas:keys>");
                        xml.AppendLine("      </aas:assetRef>");
                    }
                    
                    // Add submodel references
                    xml.AppendLine("      <aas:submodelRefs>");
                    foreach (var rel in assetSubmodelRelationships.Where(r => r.GetValueOrDefault("asset_id", "").ToString() == assetId))
                    {
                        var submodelId = rel.GetValueOrDefault("submodel_id", "").ToString();
                        xml.AppendLine("        <aas:submodelRef>");
                        xml.AppendLine("          <aas:keys>");
                        xml.AppendLine($"            <aas:key type=\"Submodel\" local=\"true\" idType=\"URI\">{submodelId}</aas:key>");
                        xml.AppendLine("          </aas:keys>");
                        xml.AppendLine("        </aas:submodelRef>");
                    }
                    xml.AppendLine("      </aas:submodelRefs>");
                    xml.AppendLine("      <aas:conceptDictionaries />");
                    xml.AppendLine("    </aas:assetAdministrationShell>");
                    break; // Only generate one AAS for now
                }
            }
            xml.AppendLine("  </aas:assetAdministrationShells>");
            
            // Generate Assets
            xml.AppendLine("  <aas:assets>");
            foreach (var asset in assets)
            {
                xml.AppendLine("    <aas:asset>");
                xml.AppendLine($"      <aas:idShort>{asset.GetValueOrDefault("idShort", "")}</aas:idShort>");
                xml.AppendLine($"      <aas:category>{asset.GetValueOrDefault("category", "")}</aas:category>");
                xml.AppendLine($"      <aas:identification idType=\"URI\">{asset.GetValueOrDefault("id", "")}</aas:identification>");
                xml.AppendLine($"      <aas:kind>{asset.GetValueOrDefault("kind", "Instance")}</aas:kind>");
                
                // Add asset identification model reference
                var firstSubmodel = submodels.FirstOrDefault();
                if (firstSubmodel != null)
                {
                    xml.AppendLine("      <aas:assetIdentificationModelRef>");
                    xml.AppendLine("        <aas:keys>");
                    xml.AppendLine($"          <aas:key type=\"Submodel\" local=\"true\" idType=\"URI\">{firstSubmodel.GetValueOrDefault("id", "")}</aas:key>");
                    xml.AppendLine("        </aas:keys>");
                    xml.AppendLine("      </aas:assetIdentificationModelRef>");
                }
                
                xml.AppendLine("    </aas:asset>");
            }
            xml.AppendLine("  </aas:assets>");
            
            // Generate Submodels
            xml.AppendLine("  <aas:submodels>");
            foreach (var submodel in submodels)
            {
                xml.AppendLine("    <aas:submodel>");
                xml.AppendLine($"      <aas:idShort>{submodel.GetValueOrDefault("idShort", "")}</aas:idShort>");
                xml.AppendLine($"      <aas:category>{submodel.GetValueOrDefault("category", "CONSTANT")}</aas:category>");
                xml.AppendLine($"      <aas:identification idType=\"URI\">{submodel.GetValueOrDefault("id", "")}</aas:identification>");
                xml.AppendLine($"      <aas:kind>{submodel.GetValueOrDefault("kind", "Instance")}</aas:kind>");
                xml.AppendLine("      <aas:qualifier />");
                
                // Add submodel elements based on file relationships
                var submodelId = submodel.GetValueOrDefault("id", "").ToString();
                var relatedFiles = fileRelationships.Where(f => f.GetValueOrDefault("element_id", "").ToString() == submodelId);
                
                if (relatedFiles.Any())
                {
                    xml.AppendLine("      <aas:submodelElements>");
                    xml.AppendLine("        <aas:submodelElement>");
                    xml.AppendLine("          <aas:submodelElementCollection>");
                    xml.AppendLine("            <aas:idShort>OperatingManual</aas:idShort>");
                    xml.AppendLine("            <aas:category />");
                    xml.AppendLine("            <aas:kind>Instance</aas:kind>");
                    xml.AppendLine("            <aas:qualifier />");
                    xml.AppendLine("            <aas:value>");
                    
                    foreach (var fileRel in relatedFiles)
                    {
                        xml.AppendLine("              <aas:submodelElement>");
                        xml.AppendLine("                <aas:file>");
                        xml.AppendLine($"                  <aas:idShort>{fileRel.GetValueOrDefault("element_idShort", "")}</aas:idShort>");
                        xml.AppendLine("                  <aas:category>PARAMETER</aas:category>");
                        xml.AppendLine("                  <aas:kind>Instance</aas:kind>");
                        xml.AppendLine("                  <aas:qualifier />");
                        xml.AppendLine("                  <aas:mimeType>application/pdf</aas:mimeType>");
                        xml.AppendLine($"                  <aas:value>{fileRel.GetValueOrDefault("file_path", "")}</aas:value>");
                        xml.AppendLine("                </aas:file>");
                        xml.AppendLine("              </aas:submodelElement>");
                    }
                    
                    xml.AppendLine("            </aas:value>");
                    xml.AppendLine("            <aas:ordered>false</aas:ordered>");
                    xml.AppendLine("            <aas:allowDuplicates>false</aas:allowDuplicates>");
                    xml.AppendLine("          </aas:submodelElementCollection>");
                    xml.AppendLine("        </aas:submodelElement>");
                    xml.AppendLine("      </aas:submodelElements>");
                }
                
                xml.AppendLine("    </aas:submodel>");
            }
            xml.AppendLine("  </aas:submodels>");
            
            xml.AppendLine("  <aas:conceptDescriptions />");
            xml.AppendLine("</aas:aasenv>");
            
            Console.WriteLine("AAS XML generated successfully from structured data");
            return xml.ToString();
        }

        /// <summary>
        /// Create AASX package from structured data using documents directory
        /// </summary>
        private string CreateAasxPackageFromStructured(string aasXml, Dictionary<string, Dictionary<string, object>> embeddedFiles, string jsonFilePath, string outputPath)
        {
            Console.WriteLine("Creating AASX package from structured data...");
            
            var aasxFileName = Path.GetFileNameWithoutExtension(outputPath) + "_from_structured.aasx";
            var aasxFilePath = Path.Combine(Path.GetDirectoryName(outputPath) ?? ".", aasxFileName);
            
            // Use the JSON file path to find the documents directory
            var jsonFileName = Path.GetFileNameWithoutExtension(jsonFilePath);
            var documentsDir = Path.Combine(Path.GetDirectoryName(jsonFilePath) ?? ".", jsonFileName + "_documents");
            
            using (var package = System.IO.Packaging.Package.Open(aasxFilePath, FileMode.Create))
            {
                var addedUris = new HashSet<string>();
                
                // Add [Content_Types].xml (required for AASX)
                var contentTypesUri = new Uri("/[Content_Types].xml", UriKind.Relative);
                var contentTypesPart = package.CreatePart(contentTypesUri, "application/vnd.openxmlformats-package.content-types");
                addedUris.Add(contentTypesUri.ToString());
                using (var stream = contentTypesPart.GetStream())
                using (var writer = new StreamWriter(stream))
                {
                    writer.Write(@"<?xml version=""1.0"" encoding=""UTF-8"" standalone=""yes""?>
<Types xmlns=""http://schemas.openxmlformats.org/package/2006/content-types"">
  <Default Extension=""xml"" ContentType=""application/xml""/>
  <Default Extension=""rels"" ContentType=""application/vnd.openxmlformats-package.relationships+xml""/>
  <Default Extension=""pdf"" ContentType=""application/pdf""/>
  <Default Extension=""jpg"" ContentType=""image/jpeg""/>
  <Default Extension=""png"" ContentType=""image/png""/>
  <Override PartName=""/aasx/customer_com_aas_9175_7013_7091_9168/customer_com_aas_9175_7013_7091_9168.aas.xml"" ContentType=""application/xml""/>
</Types>");
                }
                
                // Add AAS XML file
                var aasXmlUri = new Uri("/aasx/customer_com_aas_9175_7013_7091_9168/customer_com_aas_9175_7013_7091_9168.aas.xml", UriKind.Relative);
                var aasXmlPart = package.CreatePart(aasXmlUri, "application/xml");
                addedUris.Add(aasXmlUri.ToString());
                using (var stream = aasXmlPart.GetStream())
                using (var writer = new StreamWriter(stream))
                {
                    writer.Write(aasXml);
                }
                
                // Add AASX origin file (required)
                var aasxOriginUri = new Uri("/aasx/aasx-origin", UriKind.Relative);
                var aasxOriginPart = package.CreatePart(aasxOriginUri, "application/xml");
                addedUris.Add(aasxOriginUri.ToString());
                using (var stream = aasxOriginPart.GetStream())
                using (var writer = new StreamWriter(stream))
                {
                    writer.Write("Intentionally empty.");
                }
                
                // Add embedded files from documents directory
                Console.WriteLine($"Looking for documents in: {documentsDir}");
                Console.WriteLine($"Documents directory exists: {Directory.Exists(documentsDir)}");
                
                foreach (var file in embeddedFiles)
                {
                    var filePath = file.Key;
                    var fileInfo = file.Value;
                    
                    // Skip .rels files - they will be created automatically by System.IO.Packaging
                    if (filePath.EndsWith(".rels"))
                    {
                        Console.WriteLine($"Skipping .rels file (will be created automatically): {filePath}");
                        continue;
                    }
                    
                    // Ensure file path starts with forward slash
                    var normalizedPath = filePath.StartsWith("/") ? filePath : "/" + filePath;
                    
                    // Skip if URI already added
                    if (addedUris.Contains(normalizedPath))
                    {
                        Console.WriteLine($"Skipping duplicate file: {filePath}");
                        continue;
                    }
                    
                    // Create file part
                    var fileUri = new Uri(normalizedPath, UriKind.Relative);
                    var filePart = package.CreatePart(fileUri, GetMimeType(filePath));
                    addedUris.Add(normalizedPath);
                    
                    // Read file content from documents directory
                    var sourceFilePath = Path.Combine(documentsDir, filePath);
                    Console.WriteLine($"Looking for file: {sourceFilePath}");
                    Console.WriteLine($"File exists: {File.Exists(sourceFilePath)}");
                    
                    if (File.Exists(sourceFilePath))
                    {
                        using (var stream = filePart.GetStream())
                        using (var sourceStream = File.OpenRead(sourceFilePath))
                        {
                            sourceStream.CopyTo(stream);
                        }
                        var fileSize = new FileInfo(sourceFilePath).Length;
                        Console.WriteLine($"Restored file from documents: {filePath} ({fileSize} bytes)");
                    }
                    else
                    {
                        // Fallback to placeholder if file not found
                        using (var stream = filePart.GetStream())
                        {
                            var placeholder = $"Placeholder for {filePath}";
                            var bytes = System.Text.Encoding.UTF8.GetBytes(placeholder);
                            stream.Write(bytes, 0, bytes.Length);
                        }
                        Console.WriteLine($"Created placeholder for: {filePath} (not found in documents)");
                    }
                }
                
                // Add package relationships
                try
                {
                    // Main package relationship to AASX origin
                    package.CreateRelationship(aasxOriginUri, System.IO.Packaging.TargetMode.Internal, 
                        "http://www.admin-shell.io/aasx/relationships/aasx-origin", "R12bde8fb28b34ec1");
                    
                    // AASX origin relationship to AAS XML
                    var originPart = package.GetPart(aasxOriginUri);
                    originPart.CreateRelationship(aasXmlUri, System.IO.Packaging.TargetMode.Internal,
                        "http://www.admin-shell.io/aasx/relationships/aas-spec", "R01772d4b0ae04caf");
                    
                    // Add thumbnail relationship if image exists
                    var thumbnailFile = embeddedFiles.Keys.FirstOrDefault(f => f.EndsWith(".jpg") || f.EndsWith(".png"));
                    if (!string.IsNullOrEmpty(thumbnailFile))
                    {
                        var normalizedThumbnailPath = thumbnailFile.StartsWith("/") ? thumbnailFile : "/" + thumbnailFile;
                        var thumbnailUri = new Uri(normalizedThumbnailPath, UriKind.Relative);
                        package.CreateRelationship(thumbnailUri, System.IO.Packaging.TargetMode.Internal, 
                            "http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail", "R92817f98ba814a00");
                    }
                    
                    Console.WriteLine("Package relationships added successfully");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Warning: Could not add package relationships: {ex.Message}");
                }
            }
            
            Console.WriteLine($"AASX package created: {aasxFilePath}");
            return aasxFilePath;
        }

        /// <summary>
        /// Get MIME type for file extension
        /// </summary>
        private string GetMimeType(string filePath)
        {
            var extension = Path.GetExtension(filePath).ToLower();
            return extension switch
            {
                ".pdf" => "application/pdf",
                ".jpg" => "image/jpeg",
                ".jpeg" => "image/jpeg",
                ".png" => "image/png",
                ".xml" => "application/xml",
                ".json" => "application/json",
                _ => "application/octet-stream"
            };
        }

        /// <summary>
        /// Add package relationships
        /// </summary>
        private void AddPackageRelationships(System.IO.Packaging.Package package, Uri aasXmlUri, List<string> embeddedFiles)
        {
            try
            {
                // Add main relationship to package root
                var mainRel = package.CreateRelationship(aasXmlUri, System.IO.Packaging.TargetMode.Internal, 
                    "http://www.admin-shell.io/aasx/relationships/aas-spec", "r1");
                
                // Add thumbnail relationship if image exists
                var thumbnailFile = embeddedFiles.FirstOrDefault(f => f.EndsWith(".jpg") || f.EndsWith(".png"));
                if (!string.IsNullOrEmpty(thumbnailFile))
                {
                    var normalizedThumbnailPath = thumbnailFile.StartsWith("/") ? thumbnailFile : "/" + thumbnailFile;
                    var thumbnailUri = new Uri(normalizedThumbnailPath, UriKind.Relative);
                    package.CreateRelationship(thumbnailUri, System.IO.Packaging.TargetMode.Internal, 
                        "http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail", "r2");
                }
                
                Console.WriteLine("Package relationships added successfully");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Could not add package relationships: {ex.Message}");
            }
        }
    }
}