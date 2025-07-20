using System;
using System.IO;
using System.Text.Json;

namespace AasProcessor
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Usage:");
                Console.WriteLine("  AasProcessor process <aasx-file-path> [output-json-path]");
                Console.WriteLine("  AasProcessor process-enhanced <aasx-file-path> [output-json-path]");
                Console.WriteLine("  AasProcessor generate --json <json-data> --output <output-path> [--embedded <embedded-files>]");
                Console.WriteLine("Examples:");
                Console.WriteLine("  AasProcessor process Example_AAS_ServoDCMotor_21.aasx output.json");
                Console.WriteLine("  AasProcessor process-enhanced Example_AAS_ServoDCMotor_21.aasx output_enhanced.json");
                Console.WriteLine("  AasProcessor generate --json '{\"assets\":[]}' --output test.aasx");
                return;
            }

            string command = args[0];

            if (command == "process")
            {
                ProcessAasxCommand(args);
            }
            else if (command == "process-enhanced")
            {
                ProcessAasxEnhancedCommand(args);
            }
            else if (command == "generate")
            {
                GenerateAasxCommand(args);
            }
            else
            {
                Console.WriteLine($"Unknown command: {command}");
                Console.WriteLine("Use 'process', 'process-enhanced', or 'generate'");
                Environment.Exit(1);
            }
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
                string result = processor.ProcessAasxFileEnhanced(aasxFilePath);

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