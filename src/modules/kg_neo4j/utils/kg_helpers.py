"""
Knowledge Graph Helper Utilities

Utility functions and helper classes for Knowledge Graph operations.
Provides common functionality used across the module.
"""

import re
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def generate_graph_id(file_id: str, prefix: str = "kg") -> str:
    """
    Generate a unique graph ID based on file ID and timestamp.
    
    Args:
        file_id: The source file ID
        prefix: Prefix for the graph ID (default: "kg")
    
    Returns:
        A unique graph ID string
    """
    try:
        timestamp = datetime.now(timezone.utc)
        timestamp_str = str(int(timestamp.timestamp()))
        
        # Create a hash of the file_id for uniqueness
        file_hash = hashlib.md5(file_id.encode()).hexdigest()[:8]
        
        # Combine prefix, timestamp, and file hash
        graph_id = f"{prefix}_{timestamp_str}_{file_hash}"
        
        logger.debug(f"Generated graph ID: {graph_id} for file: {file_id}")
        return graph_id
        
    except Exception as e:
        logger.error(f"Failed to generate graph ID: {e}")
        # Fallback to simple timestamp-based ID
        fallback_id = f"{prefix}_{int(datetime.now(timezone.utc).timestamp())}"
        logger.warning(f"Using fallback graph ID: {fallback_id}")
        return fallback_id


def validate_graph_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate graph configuration parameters.
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        # Required fields
        required_fields = ["graph_name", "graph_type", "graph_category"]
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate graph type
        valid_graph_types = ["knowledge", "semantic", "conceptual", "operational", "analytical"]
        if "graph_type" in config and config["graph_type"] not in valid_graph_types:
            errors.append(f"Invalid graph_type: {config['graph_type']}. Must be one of: {valid_graph_types}")
        
        # Validate graph category
        valid_categories = ["industrial", "research", "commercial", "academic", "government", "other"]
        if "graph_category" in config and config["graph_category"] not in valid_categories:
            errors.append(f"Invalid graph_category: {config['graph_category']}. Must be one of: {valid_categories}")
        
        # Validate priority
        if "graph_priority" in config:
            try:
                priority = int(config["graph_priority"])
                if priority < 1 or priority > 10:
                    errors.append("graph_priority must be between 1 and 10")
            except (ValueError, TypeError):
                errors.append("graph_priority must be an integer")
        
        # Validate tags
        if "tags" in config and not isinstance(config["tags"], list):
            errors.append("tags must be a list")
        
        # Validate custom attributes
        if "custom_attributes" in config and not isinstance(config["custom_attributes"], dict):
            errors.append("custom_attributes must be a dictionary")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Graph configuration validation failed: {errors}")
        else:
            logger.debug("Graph configuration validation passed")
        
        return is_valid, errors
        
    except Exception as e:
        logger.error(f"Error during graph configuration validation: {e}")
        errors.append(f"Validation error: {str(e)}")
        return False, errors


def sanitize_graph_name(name: str) -> str:
    """
    Sanitize graph name for safe use in systems.
    
    Args:
        name: Raw graph name
    
    Returns:
        Sanitized graph name
    """
    try:
        if not name:
            return "unnamed_graph"
        
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Replace multiple spaces/underscores with single underscore
        sanitized = re.sub(r'[_\s]+', '_', sanitized)
        
        # Remove leading/trailing underscores and spaces
        sanitized = sanitized.strip('_ ')
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            sanitized = "unnamed_graph"
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:97] + "..."
        
        logger.debug(f"Sanitized graph name: '{name}' -> '{sanitized}'")
        return sanitized
        
    except Exception as e:
        logger.error(f"Error sanitizing graph name '{name}': {e}")
        return "unnamed_graph"


def format_timestamp(timestamp: Optional[datetime] = None, format_type: str = "iso") -> str:
    """
    Format timestamp in various formats.
    
    Args:
        timestamp: Datetime object to format (default: current time)
        format_type: Format type ("iso", "human", "short", "unix")
    
    Returns:
        Formatted timestamp string
    """
    try:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        if format_type == "iso":
            return timestamp.isoformat()
        elif format_type == "human":
            return timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
        elif format_type == "short":
            return timestamp.strftime("%Y-%m-%d %H:%M")
        elif format_type == "unix":
            return str(int(timestamp.timestamp()))
        else:
            logger.warning(f"Unknown format type: {format_type}, using ISO format")
            return timestamp.isoformat()
            
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return datetime.now(timezone.utc).isoformat()


def calculate_health_score(
    response_time: float,
    error_rate: float,
    uptime_percentage: float,
    cpu_usage: float,
    memory_usage: float
) -> float:
    """
    Calculate overall health score based on various metrics.
    
    Args:
        response_time: Response time in milliseconds
        error_rate: Error rate as percentage (0-100)
        uptime_percentage: Uptime percentage (0-100)
        cpu_usage: CPU usage percentage (0-100)
        memory_usage: Memory usage percentage (0-100)
    
    Returns:
        Health score (0-100, where 100 is perfect health)
    """
    try:
        # Normalize and weight different metrics
        response_score = max(0, 100 - (response_time / 10))  # 0ms = 100, 1000ms = 0
        error_score = max(0, 100 - error_rate)  # 0% errors = 100, 100% errors = 0
        uptime_score = uptime_percentage  # Direct mapping
        resource_score = max(0, 100 - max(cpu_usage, memory_usage))  # Lower usage = higher score
        
        # Weighted average (can be adjusted based on importance)
        weights = {
            'response_time': 0.25,
            'error_rate': 0.30,
            'uptime': 0.25,
            'resources': 0.20
        }
        
        health_score = (
            response_score * weights['response_time'] +
            error_score * weights['error_rate'] +
            uptime_score * weights['uptime'] +
            resource_score * weights['resources']
        )
        
        # Ensure score is within bounds
        health_score = max(0, min(100, health_score))
        
        logger.debug(f"Calculated health score: {health_score:.2f}")
        return round(health_score, 2)
        
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        return 50.0  # Default neutral score


def parse_graph_query(query: str) -> Dict[str, Any]:
    """
    Parse and validate graph query parameters.
    
    Args:
        query: Query string to parse
    
    Returns:
        Parsed query parameters dictionary
    """
    try:
        parsed = {
            "original_query": query,
            "query_type": "unknown",
            "parameters": {},
            "is_valid": False,
            "errors": []
        }
        
        if not query or not query.strip():
            parsed["errors"].append("Empty query")
            return parsed
        
        query_upper = query.upper().strip()
        
        # Detect query type
        if "MATCH" in query_upper:
            parsed["query_type"] = "match"
        elif "CREATE" in query_upper:
            parsed["query_type"] = "create"
        elif "DELETE" in query_upper:
            parsed["query_type"] = "delete"
        elif "SET" in query_upper:
            parsed["query_type"] = "update"
        elif "MERGE" in query_upper:
            parsed["query_type"] = "merge"
        else:
            parsed["errors"].append("Unknown query type")
        
        # Basic validation
        if "DROP" in query_upper or "DELETE DATABASE" in query_upper:
            parsed["errors"].append("Dangerous operation detected")
        
        # Extract parameters (basic extraction)
        param_pattern = r'\$(\w+)'
        params = re.findall(param_pattern, query)
        parsed["parameters"] = {param: None for param in params}
        
        parsed["is_valid"] = len(parsed["errors"]) == 0
        
        logger.debug(f"Parsed query: {parsed}")
        return parsed
        
    except Exception as e:
        logger.error(f"Error parsing graph query: {e}")
        return {
            "original_query": query,
            "query_type": "unknown",
            "parameters": {},
            "is_valid": False,
            "errors": [f"Parse error: {str(e)}"]
        }


def validate_neo4j_connection_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate Neo4j connection configuration.
    
    Args:
        config: Connection configuration dictionary
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        # Required fields
        required_fields = ["host", "port", "username", "password", "database"]
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate host
        if "host" in config and config["host"]:
            host = config["host"]
            if not re.match(r'^[a-zA-Z0-9.-]+$', host) and host != "localhost":
                errors.append("Invalid host format")
        
        # Validate port
        if "port" in config and config["port"]:
            try:
                port = int(config["port"])
                if port < 1 or port > 65535:
                    errors.append("Port must be between 1 and 65535")
            except (ValueError, TypeError):
                errors.append("Port must be a valid integer")
        
        # Validate database name
        if "database" in config and config["database"]:
            db_name = config["database"]
            if not re.match(r'^[a-zA-Z0-9_-]+$', db_name):
                errors.append("Invalid database name format")
        
        # Validate SSL settings
        if "ssl_enabled" in config and config["ssl_enabled"]:
            if "ssl_cert_file" in config and not config["ssl_cert_file"]:
                errors.append("SSL certificate file required when SSL is enabled")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Neo4j connection validation failed: {errors}")
        else:
            logger.debug("Neo4j connection validation passed")
        
        return is_valid, errors
        
    except Exception as e:
        logger.error(f"Error during Neo4j connection validation: {e}")
        errors.append(f"Validation error: {str(e)}")
        return False, errors


def calculate_performance_metrics(
    start_time: datetime,
    end_time: datetime,
    operations_count: int,
    errors_count: int
) -> Dict[str, Any]:
    """
    Calculate performance metrics from operation data.
    
    Args:
        start_time: Operation start time
        end_time: Operation end time
        operations_count: Total number of operations
        errors_count: Number of errors encountered
    
    Returns:
        Dictionary containing performance metrics
    """
    try:
        # Calculate duration
        duration = (end_time - start_time).total_seconds()
        
        # Calculate throughput
        throughput = operations_count / duration if duration > 0 else 0
        
        # Calculate error rate
        error_rate = (errors_count / operations_count * 100) if operations_count > 0 else 0
        
        # Calculate success rate
        success_rate = 100 - error_rate
        
        # Calculate average operation time
        avg_operation_time = duration / operations_count if operations_count > 0 else 0
        
        metrics = {
            "duration_seconds": round(duration, 3),
            "operations_count": operations_count,
            "errors_count": errors_count,
            "throughput_ops_per_sec": round(throughput, 2),
            "error_rate_percent": round(error_rate, 2),
            "success_rate_percent": round(success_rate, 2),
            "avg_operation_time_seconds": round(avg_operation_time, 3)
        }
        
        logger.debug(f"Calculated performance metrics: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        return {
            "duration_seconds": 0,
            "operations_count": 0,
            "errors_count": 0,
            "throughput_ops_per_sec": 0,
            "error_rate_percent": 0,
            "success_rate_percent": 0,
            "avg_operation_time_seconds": 0
        }


def generate_export_filename(
    graph_id: str,
    export_format: str,
    include_timestamp: bool = True
) -> str:
    """
    Generate filename for graph export operations.
    
    Args:
        graph_id: The graph ID
        export_format: Export format (cypher, json, graphml, csv)
        include_timestamp: Whether to include timestamp in filename
    
    Returns:
        Generated filename string
    """
    try:
        # Sanitize graph ID for filename
        safe_graph_id = re.sub(r'[<>:"/\\|?*]', '_', graph_id)
        
        # Base filename
        filename = f"kg_export_{safe_graph_id}.{export_format.lower()}"
        
        # Add timestamp if requested
        if include_timestamp:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"kg_export_{safe_graph_id}_{timestamp}.{export_format.lower()}"
        
        logger.debug(f"Generated export filename: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating export filename: {e}")
        # Fallback filename
        fallback = f"kg_export_{int(datetime.now(timezone.utc).timestamp())}.{export_format.lower()}"
        logger.warning(f"Using fallback export filename: {fallback}")
        return fallback
