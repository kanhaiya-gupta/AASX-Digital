using System;
using System.IO;
using System.Text.Json;

namespace AasProcessor
{
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
            var processor = new AasProcessor();

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
                        string result = processor.ProcessAasxFile(args[1]);
                        Console.WriteLine(result);
                        break;

                    case "process-enhanced":
                        if (args.Length < 2)
                        {
                            Console.WriteLine("Error: Input AASX file path required for 'process-enhanced' command.");
                            ShowUsage();
                            return;
                        }
                        string outputPath = args.Length > 2 ? args[2] : null;
                        string enhancedResult = processor.ProcessAasxFileEnhanced(args[1], outputPath);
                        
                        // Save JSON output to file if output path is provided
                        if (!string.IsNullOrEmpty(outputPath))
                        {
                            try
                            {
                                File.WriteAllText(outputPath, enhancedResult);
                                Console.WriteLine($"JSON output saved to: {outputPath}");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Warning: Could not save JSON to {outputPath}: {ex.Message}");
                                Console.WriteLine("Output:");
                                Console.WriteLine(enhancedResult);
                            }
                        }
                        else
                        {
                            Console.WriteLine(enhancedResult);
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
                        
                        // Check for embedded files parameter
                        for (int i = 3; i < args.Length; i++)
                        {
                            if (args[i] == "--embedded-files" && i + 1 < args.Length)
                            {
                                embeddedFiles = args[i + 1];
                                break;
                            }
                        }
                        
                        var embeddedFilesDict = ParseEmbeddedFiles(embeddedFiles);
                        string generateResult = processor.GenerateAasxFile(jsonData, generateOutputPath, embeddedFilesDict);
                        Console.WriteLine(generateResult);
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
                        
                        // Read JSON file content
                        if (!File.Exists(jsonFilePath))
                        {
                            Console.WriteLine($"Error: JSON file not found: {jsonFilePath}");
                            return;
                        }
                        
                        string jsonContent = File.ReadAllText(jsonFilePath);
                        string structuredResult = processor.GenerateAasxFileFromStructured(jsonContent, jsonFilePath, structuredOutputPath);
                        Console.WriteLine(structuredResult);
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
            Console.WriteLine("Examples:");
            Console.WriteLine("  AasProcessor process-enhanced data/example.aasx output/result");
            Console.WriteLine("  AasProcessor generate-structured output/result.json output/reconstructed.aasx");
            Console.WriteLine();
            Console.WriteLine("Document Structure:");
            Console.WriteLine("  Forward:  AASX → JSON + _documents/ folder");
            Console.WriteLine("  Backward: JSON + _documents/ folder → AASX");
        }

        static void ProcessAasxCommand(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: AasProcessor process <aasx-file-path> [output-json-path]");
                return;
            }

            string aasxFilePath = args[1];
            string? outputPath = args.Length > 2 ? args[2] : null;

            try
            {
                var processor = new AasProcessor();
                string result = processor.ProcessAasxFile(aasxFilePath);

                if (outputPath != null)
                {
                    File.WriteAllText(outputPath, result);
                    Console.WriteLine($"AASX data exported to: {outputPath}");
                }
                else
                {
                    Console.WriteLine(result);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }

        static void ProcessAasxEnhancedCommand(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: AasProcessor process-enhanced <aasx-file-path> [output-json-path]");
                return;
            }

            string aasxFilePath = args[1];
            string? outputPath = args.Length > 2 ? args[2] : null;

            try
            {
                var processor = new AasProcessor();
                string result = processor.ProcessAasxFileEnhanced(aasxFilePath, outputPath);

                if (outputPath != null)
                {
                    File.WriteAllText(outputPath, result);
                    Console.WriteLine($"Enhanced AASX data exported to: {outputPath}");
                }
                else
                {
                    Console.WriteLine(result);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }

        static void GenerateAasxCommand(string[] args)
        {
            string? jsonData = null;
            string? outputPath = null;
            string? embeddedFiles = null;

            // Parse arguments
            for (int i = 1; i < args.Length; i += 2)
            {
                if (i + 1 >= args.Length) break;

                switch (args[i])
                {
                    case "--json":
                        jsonData = args[i + 1];
                        break;
                    case "--output":
                        outputPath = args[i + 1];
                        break;
                    case "--embedded":
                        embeddedFiles = args[i + 1];
                        break;
                }
            }

            if (jsonData == null || outputPath == null)
            {
                Console.WriteLine("Error: --json and --output are required for generation");
                return;
            }

            try
            {
                var processor = new AasProcessor();
                
                // Parse embedded files if provided
                var embeddedFilesDict = ParseEmbeddedFiles(embeddedFiles);
                
                string result = processor.GenerateAasxFile(jsonData, outputPath, embeddedFilesDict);
                Console.WriteLine(result);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }

        static void GenerateAasxFromStructuredCommand(string[] args)
        {
            string? jsonFilePath = null;
            string? outputPath = null;

            // Parse arguments
            for (int i = 1; i < args.Length; i += 2)
            {
                if (i + 1 >= args.Length) break;

                switch (args[i])
                {
                    case "--json":
                        jsonFilePath = args[i + 1];
                        break;
                    case "--output":
                        outputPath = args[i + 1];
                        break;
                }
            }

            if (jsonFilePath == null || outputPath == null)
            {
                Console.WriteLine("Error: --json and --output are required for structured generation");
                return;
            }

            try
            {
                // Read JSON file
                string jsonData = File.ReadAllText(jsonFilePath);
                
                var processor = new AasProcessor();
                string result = processor.GenerateAasxFileFromStructured(jsonData, jsonFilePath, outputPath);
                Console.WriteLine($"Generated AASX file: {result}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
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
    }
} 