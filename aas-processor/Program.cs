using System;
using System.IO;
using System.Text.Json;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using AasProcessor.Extraction;
using AasProcessor.Xml;
using AasProcessor.Packaging;
using AasProcessor.Utils;
using AasProcessor.Processing;

namespace AasProcessor
{
    /// <summary>
    /// Main entry point and command-line interface for the modular AAS processor framework.
    /// 
    /// This class provides the primary command-line interface for the AAS processor, offering
    /// multiple processing modes and output formats for AASX package analysis and conversion.
    /// It serves as the main application entry point and demonstrates the usage of the modular
    /// processor architecture.
    /// 
    /// <para>
    /// <strong>Command-Line Interface:</strong>
    /// <list type="bullet">
    /// <item><description><strong>process:</strong> Basic AASX processing with JSON/YAML output</description></item>
    /// <item><description><strong>process-enhanced:</strong> Enhanced processing with complete relationship mapping</description></item>
    /// <item><description><strong>generate:</strong> Backward processing from JSON to AASX</description></item>
    /// <item><description><strong>extract-xml:</strong> Extract AAS XML content from AASX packages</description></item>
    /// <item><description><strong>help:</strong> Display usage information and command options</description></item>
    /// </list>
    /// </para>
    /// 
    /// <para>
    /// <strong>Processing Modes:</strong>
    /// <list type="bullet">
    /// <item><description><strong>Basic Processing:</strong> Core AAS data extraction with file categorization</description></item>
    /// <item><description><strong>Enhanced Processing:</strong> Complete extraction with relationships and concept descriptions</description></item>
    /// <item><description><strong>Backward Processing:</strong> AASX reconstruction from structured data</description></item>
    /// <item><description><strong>XML Extraction:</strong> Direct AAS XML content extraction</description></item>
    /// </list>
    /// </para>
    /// 
    /// <para>
    /// <strong>Output Formats:</strong>
    /// <list type="bullet">
    /// <item><description><strong>JSON:</strong> Structured data with complete AAS information</description></item>
    /// <item><description><strong>YAML:</strong> Human-readable structured data format</description></item>
    /// <item><description><strong>AASX:</strong> Reconstructed AASX packages</description></item>
    /// <item><description><strong>XML:</strong> Extracted AAS XML content</description></item>
    /// </list>
    /// </para>
    /// </summary>
    /// 
    /// <remarks>
    /// This program demonstrates the complete modular AAS processor framework, showcasing
    /// the integration of all modular components for comprehensive AASX processing workflows.
    /// 
    /// <para>
    /// <strong>Modular Architecture Integration:</strong>
    /// The program leverages all modular components:
    /// <list type="bullet">
    /// <item><description><see cref="AasProcessor.Processing.AasProcessorModular"/> - Main processing logic</description></item>
    /// <item><description><see cref="AasProcessor.Extraction.AasExtractor"/> - AAS data extraction</description></item>
    /// <item><description><see cref="AasProcessor.Packaging.AasxPackageWriter"/> - AASX package creation</description></item>
    /// <item><description><see cref="AasProcessor.Xml.AasXmlGenerator"/> - XML content generation</description></item>
    /// <item><description><see cref="AasProcessor.Utils.Versioning"/> - Version detection and namespace management</description></item>
    /// </list>
    /// </para>
    /// 
    /// <para>
    /// <strong>Error Handling:</strong>
    /// Comprehensive error handling ensures that all processing errors are reported with
    /// detailed information for debugging and recovery. The program gracefully handles
    /// file access issues, malformed AASX packages, and processing errors.
    /// </para>
    /// 
    /// <para>
    /// <strong>Output Management:</strong>
    /// The program automatically manages output files and directories, creating necessary
    /// directory structures and handling file naming conventions. It supports both
    /// console output and file-based output with automatic format detection.
    /// </para>
    /// </remarks>
    /// 
    /// <example>
    /// <code>
    /// // Basic AASX processing
    /// AasProcessor.exe process "input.aasx" "output.json"
    /// 
    /// // Enhanced processing with custom output
    /// AasProcessor.exe process-enhanced "input.aasx" "enhanced_output.json"
    /// 
    /// // Backward processing from JSON to AASX
    /// AasProcessor.exe generate "input.json" "reconstructed.aasx"
    /// 
    /// // Extract AAS XML content
    /// AasProcessor.exe extract-xml "input.aasx" "extracted.xml"
    /// 
    /// // Display help information
    /// AasProcessor.exe help
    /// </code>
    /// </example>
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                ShowUsage();
                return;
            }

            var command = args[0].ToLower();

            try
            {
                switch (command)
                {
                    case "process":
                        if (args.Length < 2)
                        {
                            Console.WriteLine("Error: Input AASX file path required for 'process' command.");
                            ShowUsage();
                            return;
                        }
                        string aasxFilePath = args[1];
                        string? outputPath = args.Length > 2 ? args[2] : null;
                        try
                        {
                            // Use the new modular processing class
                            string resultProcess = AasProcessorModular.ProcessAasxFile(aasxFilePath, outputPath);
                            if (!string.IsNullOrEmpty(outputPath))
                            {
                                File.WriteAllText(outputPath, resultProcess);
                                Console.WriteLine($"AASX data exported to: {outputPath}");
                                // Also write YAML if output is .json
                                if (outputPath.EndsWith(".json"))
                                {
                                    var jsonDoc = System.Text.Json.JsonDocument.Parse(resultProcess);
                                    var dotNetObj = ConvertJsonElement(jsonDoc.RootElement);
                                    var yamlSerializer = new SerializerBuilder()
                                        .WithNamingConvention(CamelCaseNamingConvention.Instance)
                                        .Build();
                                    var yaml = yamlSerializer.Serialize(dotNetObj);
                                    var yamlPath = outputPath.Substring(0, outputPath.Length - 5) + ".yaml";
                                    File.WriteAllText(yamlPath, yaml);
                                    Console.WriteLine($"AASX data also exported to: {yamlPath}");
                                }
                            }
                            else
                            {
                                Console.WriteLine(resultProcess);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error: {ex.Message}");
                            Environment.Exit(1);
                        }
                        break;

                    case "process-enhanced":
                        if (args.Length < 2)
                        {
                            Console.WriteLine("Error: Input AASX file path required for 'process-enhanced' command.");
                            ShowUsage();
                            return;
                        }
                        string enhancedAasxFilePath = args[1];
                        string? enhancedOutputPath = args.Length > 2 ? args[2] : null;
                        try
                        {
                            // Use the new modular processing class
                            string enhancedResult = AasProcessorModular.ProcessAasxFileEnhanced(enhancedAasxFilePath, enhancedOutputPath);
                            if (!string.IsNullOrEmpty(enhancedOutputPath))
                            {
                                File.WriteAllText(enhancedOutputPath, enhancedResult);
                                Console.WriteLine($"Enhanced AASX data exported to: {enhancedOutputPath}");
                            }
                            else
                            {
                                Console.WriteLine(enhancedResult);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error: {ex.Message}");
                            Environment.Exit(1);
                        }
                        break;

                    case "generate":
                        if (args.Length < 3)
                        {
                            Console.WriteLine("Error: JSON data and output path required for 'generate' command.");
                            ShowUsage();
                            return;
                        }
                        string jsonData = args[1];
                        string generateOutputPath = args[2];
                        string? embeddedFiles = null;
                        for (int i = 3; i < args.Length; i++)
                        {
                            if (args[i] == "--embedded-files" && i + 1 < args.Length)
                            {
                                embeddedFiles = args[i + 1];
                                break;
                            }
                        }
                        var embeddedFilesDict = ParseEmbeddedFiles(embeddedFiles);
                        // Use modular XML generator and packager
                        var aasDataGenerate = JsonSerializer.Deserialize<JsonElement>(jsonData);
                        string aasXmlGenerate = AasXmlGenerator.GenerateAasXml(aasDataGenerate);
                        string resultGenerate = AasxPackageWriter.CreateAasxPackageFromStructured(aasXmlGenerate, null, null, generateOutputPath);
                        Console.WriteLine(resultGenerate);
                        break;

                    case "generate-structured":
                        if (args.Length < 3)
                        {
                            Console.WriteLine("Error: JSON file path and output path required for 'generate-structured' command.");
                            ShowUsage();
                            return;
                        }
                        string jsonFilePath = args[1];
                        string structuredOutputPath = args[2];
                        if (!File.Exists(jsonFilePath))
                        {
                            Console.WriteLine($"Error: JSON file not found: {jsonFilePath}");
                            return;
                        }
                        string jsonContent = File.ReadAllText(jsonFilePath);
                        // Parse JSON or YAML
                        if (jsonFilePath.EndsWith(".yaml") || jsonFilePath.EndsWith(".yml"))
                        {
                            var yamlText = File.ReadAllText(jsonFilePath);
                            var deserializer = new DeserializerBuilder()
                                .WithNamingConvention(CamelCaseNamingConvention.Instance)
                                .Build();
                            var yamlObject = deserializer.Deserialize<object>(yamlText);
                            jsonContent = System.Text.Json.JsonSerializer.Serialize(yamlObject, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
                        }
                        // Use the new self-contained backward conversion method
                        string structuredResult = AasxPackageWriter.GenerateAasxFileFromStructured(jsonContent, jsonFilePath, structuredOutputPath);
                        Console.WriteLine(structuredResult);
                        break;

                    case "export-graph":
                        if (args.Length < 3)
                        {
                            Console.WriteLine("Error: Input AASX file path and output graph JSON path required for 'export-graph' command.");
                            ShowUsage();
                            return;
                        }
                        string graphAasxFilePath = args[1];
                        string graphOutputPath = args[2];
                        try
                        {
                            string graphJson = AasProcessorModular.ExportGraph(graphAasxFilePath);
                            File.WriteAllText(graphOutputPath, graphJson);
                            Console.WriteLine($"Graph data exported to: {graphOutputPath}");
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error: {ex.Message}");
                            Environment.Exit(1);
                        }
                        break;

                    case "export-rdf":
                        if (args.Length < 3)
                        {
                            Console.WriteLine("Error: Input AASX file path and output RDF/Turtle path required for 'export-rdf' command.");
                            ShowUsage();
                            return;
                        }
                        string rdfAasxFilePath = args[1];
                        string rdfOutputPath = args[2];
                        try
                        {
                            string rdfTurtle = AasProcessorModular.ExportRdf(rdfAasxFilePath);
                            File.WriteAllText(rdfOutputPath, rdfTurtle);
                            Console.WriteLine($"RDF/Turtle data exported to: {rdfOutputPath}");
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error: {ex.Message}");
                            Environment.Exit(1);
                        }
                        break;

                    default:
                        Console.WriteLine($"Error: Unknown command '{command}'.");
                        ShowUsage();
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }

        static void ShowUsage()
        {
            Console.WriteLine("AASX Package Processor - Enhanced Round-trip Conversion");
            Console.WriteLine("========================================================");
            Console.WriteLine();
            Console.WriteLine("Commands:");
            Console.WriteLine();
            Console.WriteLine("  process <aasx-file>");
            Console.WriteLine("    Process AASX file and output basic JSON");
            Console.WriteLine();
            Console.WriteLine("  process-enhanced <aasx-file> [output-path]");
            Console.WriteLine("    Process AASX file with enhanced extraction and save documents separately");
            Console.WriteLine("    Creates: output.json + output_documents/ folder");
            Console.WriteLine();
            Console.WriteLine("  generate <json-data> <output-path> [--embedded-files <files-json>]");
            Console.WriteLine("    Generate AASX from JSON data (legacy method)");
            Console.WriteLine();
            Console.WriteLine("  generate-structured <json-file> <output-path>");
            Console.WriteLine("    Generate AASX from structured JSON using documents directory");
            Console.WriteLine("    Expects: input.json + input_documents/ folder");
            Console.WriteLine();
            Console.WriteLine("  export-graph <aasx-file> <output-graph.json>");
            Console.WriteLine("    Export graph data (nodes and edges) from AASX file as JSON");
            Console.WriteLine();
            Console.WriteLine("  export-rdf <aasx-file> <output-rdf.ttl>");
            Console.WriteLine("    Export AASX data as RDF/Turtle format for semantic web applications");
            Console.WriteLine();
            Console.WriteLine("Examples:");
            Console.WriteLine("  AasProcessor process-enhanced data/example.aasx output/result");
            Console.WriteLine("  AasProcessor generate-structured output/result.json output/reconstructed.aasx");
            Console.WriteLine("  AasProcessor export-graph data/example.aasx output/graph.json");
            Console.WriteLine("  AasProcessor export-rdf data/example.aasx output/aas_data.ttl");
            Console.WriteLine();
            Console.WriteLine("Document Structure:");
            Console.WriteLine("  Forward:  AASX → JSON + _documents/ folder");
            Console.WriteLine("  Backward: JSON + _documents/ folder → AASX");
        }

        static string ExtractAasxXmlContent(string aasxFilePath)
        {
            // Prefer .aas.xml files, fallback to any .xml except [Content_Types].xml
            using (var zip = System.IO.Compression.ZipFile.OpenRead(aasxFilePath))
            {
                // 1. Try to find a .aas.xml file (main AAS XML)
                var aasXmlEntry = zip.Entries
                    .FirstOrDefault(e => e.Name.EndsWith(".aas.xml", StringComparison.OrdinalIgnoreCase));
                if (aasXmlEntry != null)
                {
                    using (var stream = aasXmlEntry.Open())
                    using (var reader = new StreamReader(stream))
                    {
                        Console.WriteLine($"[INFO] Extracting main AAS XML: {aasXmlEntry.FullName}");
                        return reader.ReadToEnd();
                    }
                }
                // 2. Fallback: any .xml file except [Content_Types].xml
                foreach (var entry in zip.Entries)
                {
                    if (entry.Name.EndsWith(".xml", StringComparison.OrdinalIgnoreCase) &&
                        !entry.Name.Equals("[Content_Types].xml", StringComparison.OrdinalIgnoreCase))
                    {
                        using (var stream = entry.Open())
                        using (var reader = new StreamReader(stream))
                        {
                            Console.WriteLine($"[INFO] Extracting fallback XML: {entry.FullName}");
                            return reader.ReadToEnd();
                        }
                    }
                }
            }
            throw new FileNotFoundException("No AAS XML content found in AASX file.");
        }

        static System.Collections.Generic.Dictionary<string, string>? ParseEmbeddedFiles(string? embeddedFiles)
        {
            if (string.IsNullOrEmpty(embeddedFiles))
                return null;
            try
            {
                return JsonSerializer.Deserialize<System.Collections.Generic.Dictionary<string, string>>(embeddedFiles);
            }
            catch
            {
                Console.WriteLine("Warning: Could not parse embedded files JSON");
                return null;
            }
        }

        static object? ConvertJsonElement(System.Text.Json.JsonElement element)
        {
            switch (element.ValueKind)
            {
                case System.Text.Json.JsonValueKind.Object:
                    var dict = new Dictionary<string, object?>();
                    foreach (var prop in element.EnumerateObject())
                        dict[prop.Name] = ConvertJsonElement(prop.Value);
                    return dict;
                case System.Text.Json.JsonValueKind.Array:
                    return element.EnumerateArray().Select(ConvertJsonElement).ToList();
                case System.Text.Json.JsonValueKind.String:
                    return element.GetString();
                case System.Text.Json.JsonValueKind.Number:
                    if (element.TryGetInt64(out long l)) return l;
                    if (element.TryGetDouble(out double d)) return d;
                    return element.GetRawText();
                case System.Text.Json.JsonValueKind.True:
                case System.Text.Json.JsonValueKind.False:
                    return element.GetBoolean();
                default:
                    return null;
            }
        }
    }
} 