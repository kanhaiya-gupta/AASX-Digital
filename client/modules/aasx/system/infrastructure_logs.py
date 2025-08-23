"""
Infrastructure Logs Service

Provides log aggregation, analysis, and monitoring for the AASX-ETL platform
with user-based access control and log filtering capabilities.
"""

import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Log entry information"""
    timestamp: datetime
    level: str
    message: str
    service: str
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None

@dataclass
class LogSummary:
    """Log summary statistics"""
    total_entries: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    time_range: Tuple[datetime, datetime]
    services: List[str]
    users: List[str]

class InfrastructureLogs:
    """Infrastructure log monitoring and analysis service with user-based access control"""
    
    def __init__(self):
        self.log_directories = [
            'logs/',
            'webapp/logs/',
            'aas-processor/logs/'
        ]
        self.max_log_size = 100 * 1024 * 1024  # 100MB
        self.log_cache: Dict[str, List[LogEntry]] = {}
        self.cache_ttl = 300  # 5 minutes
        
    def get_logs_for_user(self, user_id: str, org_id: Optional[str] = None, 
                          level: Optional[str] = None, service: Optional[str] = None,
                          hours: int = 24, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get logs filtered for specific user with access control"""
        try:
            # Get all available logs
            all_logs = self._collect_logs_from_directories()
            
            # Filter logs based on user access and parameters
            filtered_logs = self._filter_logs_for_user(
                all_logs, user_id, org_id, level, service, hours, limit
            )
            
            # Convert to dictionary format for JSON serialization
            return [asdict(log_entry) for log_entry in filtered_logs]
            
        except Exception as e:
            logger.error(f"❌ Failed to get logs for user {user_id}: {e}")
            return []
    
    def get_log_summary_for_user(self, user_id: str, org_id: Optional[str] = None, 
                                hours: int = 24) -> Dict[str, Any]:
        """Get log summary statistics for specific user"""
        try:
            logs = self._collect_logs_from_directories()
            user_logs = self._filter_logs_for_user(logs, user_id, org_id, hours=hours)
            
            if not user_logs:
                return self._get_empty_log_summary()
            
            # Calculate summary statistics
            summary = self._calculate_log_summary(user_logs)
            
            return {
                'user_id': user_id,
                'org_id': org_id,
                'period_hours': hours,
                'summary': asdict(summary),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get log summary for user {user_id}: {e}")
            return self._get_error_log_summary(user_id, org_id)
    
    def search_logs_for_user(self, user_id: str, org_id: Optional[str] = None,
                            query: str = "", level: Optional[str] = None,
                            service: Optional[str] = None, hours: int = 24,
                            limit: int = 500) -> List[Dict[str, Any]]:
        """Search logs for specific user with text query"""
        try:
            if not query.strip():
                return self.get_logs_for_user(user_id, org_id, level, service, hours, limit)
            
            # Get filtered logs
            logs = self._collect_logs_from_directories()
            user_logs = self._filter_logs_for_user(logs, user_id, org_id, level, service, hours)
            
            # Perform text search
            search_results = []
            query_lower = query.lower()
            
            for log_entry in user_logs:
                if (query_lower in log_entry.message.lower() or
                    query_lower in log_entry.service.lower() or
                    (log_entry.extra_data and any(query_lower in str(v).lower() 
                                                 for v in log_entry.extra_data.values()))):
                    search_results.append(log_entry)
                    
                    if len(search_results) >= limit:
                        break
            
            return [asdict(log_entry) for log_entry in search_results]
            
        except Exception as e:
            logger.error(f"❌ Failed to search logs for user {user_id}: {e}")
            return []
    
    def get_error_logs_for_user(self, user_id: str, org_id: Optional[str] = None,
                               hours: int = 24, limit: int = 500) -> List[Dict[str, Any]]:
        """Get error and warning logs for specific user"""
        try:
            return self.get_logs_for_user(
                user_id, org_id, level='error', hours=hours, limit=limit
            )
        except Exception as e:
            logger.error(f"❌ Failed to get error logs for user {user_id}: {e}")
            return []
    
    def get_service_logs_for_user(self, user_id: str, service: str, 
                                 org_id: Optional[str] = None, hours: int = 24,
                                 limit: int = 500) -> List[Dict[str, Any]]:
        """Get logs for specific service and user"""
        try:
            return self.get_logs_for_user(
                user_id, org_id, service=service, hours=hours, limit=limit
            )
        except Exception as e:
            logger.error(f"❌ Failed to get service logs for user {user_id}: {e}")
            return []
    
    def get_log_trends_for_user(self, user_id: str, org_id: Optional[str] = None,
                               hours: int = 24) -> Dict[str, Any]:
        """Get log trends and patterns for specific user"""
        try:
            logs = self._collect_logs_from_directories()
            user_logs = self._filter_logs_for_user(logs, user_id, org_id, hours=hours)
            
            if not user_logs:
                return self._get_empty_trends()
            
            # Calculate trends
            trends = self._calculate_log_trends(user_logs, hours)
            
            return {
                'user_id': user_id,
                'org_id': org_id,
                'period_hours': hours,
                'trends': trends,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get log trends for user {user_id}: {e}")
            return self._get_error_trends(user_id, org_id)
    
    def _collect_logs_from_directories(self) -> List[LogEntry]:
        """Collect logs from configured directories"""
        try:
            all_logs = []
            
            for log_dir in self.log_directories:
                if os.path.exists(log_dir):
                    log_files = self._find_log_files(log_dir)
                    for log_file in log_files:
                        file_logs = self._parse_log_file(log_file)
                        all_logs.extend(file_logs)
            
            # Sort by timestamp (newest first)
            all_logs.sort(key=lambda x: x.timestamp, reverse=True)
            
            return all_logs
            
        except Exception as e:
            logger.error(f"❌ Failed to collect logs from directories: {e}")
            return []
    
    def _find_log_files(self, directory: str) -> List[str]:
        """Find log files in directory"""
        try:
            log_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.log', '.txt')) or 'log' in file.lower():
                        log_files.append(os.path.join(root, file))
            return log_files
        except Exception as e:
            logger.error(f"❌ Failed to find log files in {directory}: {e}")
            return []
    
    def _parse_log_file(self, file_path: str) -> List[LogEntry]:
        """Parse individual log file"""
        try:
            log_entries = []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    log_entry = self._parse_log_line(line.strip(), file_path, line_num)
                    if log_entry:
                        log_entries.append(log_entry)
            
            return log_entries
            
        except Exception as e:
            logger.error(f"❌ Failed to parse log file {file_path}: {e}")
            return []
    
    def _parse_log_line(self, line: str, file_path: str, line_num: int) -> Optional[LogEntry]:
        """Parse individual log line"""
        try:
            if not line.strip():
                return None
            
            # Common log patterns
            patterns = [
                # Standard Python logging format
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)',
                # ISO format
                r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z?) - (\w+) - (.+)',
                # Simple timestamp format
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.+)'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    timestamp_str, level, message = match.groups()
                    
                    # Parse timestamp
                    try:
                        if 'T' in timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    except ValueError:
                        timestamp = datetime.now()
                    
                    # Extract service and user info from message
                    service, user_id, org_id, extra_data = self._extract_log_metadata(message)
                    
                    return LogEntry(
                        timestamp=timestamp,
                        level=level.lower(),
                        message=message,
                        service=service,
                        user_id=user_id,
                        org_id=org_id,
                        source_file=file_path,
                        line_number=line_num,
                        extra_data=extra_data
                    )
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to parse log line: {line[:100]}... Error: {e}")
            return None
    
    def _extract_log_metadata(self, message: str) -> Tuple[str, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
        """Extract metadata from log message"""
        try:
            service = "unknown"
            user_id = None
            org_id = None
            extra_data = {}
            
            # Extract service name
            if "AASX-ETL" in message:
                service = "aasx_etl"
            elif "database" in message.lower():
                service = "database"
            elif "auth" in message.lower():
                service = "authentication"
            
            # Extract user ID (common patterns)
            user_match = re.search(r'user[:\s]+([a-f0-9-]+)', message, re.IGNORECASE)
            if user_match:
                user_id = user_match.group(1)
            
            # Extract org ID
            org_match = re.search(r'org[:\s]+([a-f0-9-]+)', message, re.IGNORECASE)
            if org_match:
                org_id = org_match.group(1)
            
            # Extract additional data
            if "{" in message and "}" in message:
                try:
                    json_start = message.find("{")
                    json_end = message.rfind("}") + 1
                    json_str = message[json_start:json_end]
                    extra_data = json.loads(json_str)
                except:
                    pass
            
            return service, user_id, org_id, extra_data
            
        except Exception as e:
            logger.debug(f"Failed to extract log metadata: {e}")
            return "unknown", None, None, {}
    
    def _filter_logs_for_user(self, logs: List[LogEntry], user_id: str, 
                             org_id: Optional[str] = None, level: Optional[str] = None,
                             service: Optional[str] = None, hours: int = 24,
                             limit: int = 1000) -> List[LogEntry]:
        """Filter logs based on user access and parameters"""
        try:
            filtered_logs = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for log_entry in logs:
                # Time filter
                if log_entry.timestamp < cutoff_time:
                    continue
                
                # Level filter
                if level and log_entry.level != level.lower():
                    continue
                
                # Service filter
                if service and log_entry.service != service:
                    continue
                
                # User access control
                if not self._user_can_access_log(log_entry, user_id, org_id):
                    continue
                
                filtered_logs.append(log_entry)
                
                if len(filtered_logs) >= limit:
                    break
            
            return filtered_logs
            
        except Exception as e:
            logger.error(f"❌ Failed to filter logs for user {user_id}: {e}")
            return []
    
    def _user_can_access_log(self, log_entry: LogEntry, user_id: str, org_id: Optional[str] = None) -> bool:
        """Check if user can access specific log entry"""
        try:
            # User can always see their own logs
            if log_entry.user_id == user_id:
                return True
            
            # User can see organization logs if they belong to the same org
            if org_id and log_entry.org_id == org_id:
                return True
            
            # User can see system-level logs (no specific user/org)
            if not log_entry.user_id and not log_entry.org_id:
                return True
            
            # User can see core service logs
            if log_entry.service in ['database', 'authentication', 'aasx_etl']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check log access for user {user_id}: {e}")
            return False
    
    def _calculate_log_summary(self, logs: List[LogEntry]) -> LogSummary:
        """Calculate summary statistics from logs"""
        try:
            if not logs:
                return self._get_empty_log_summary()
            
            error_count = sum(1 for log in logs if log.level == 'error')
            warning_count = sum(1 for log in logs if log.level == 'warning')
            info_count = sum(1 for log in logs if log.level == 'info')
            debug_count = sum(1 for log in logs if log.level == 'debug')
            
            services = list(set(log.service for log in logs))
            users = list(set(log.user_id for log in logs if log.user_id))
            
            time_range = (min(log.timestamp for log in logs), max(log.timestamp for log in logs))
            
            return LogSummary(
                total_entries=len(logs),
                error_count=error_count,
                warning_count=warning_count,
                info_count=info_count,
                debug_count=debug_count,
                time_range=time_range,
                services=services,
                users=users
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate log summary: {e}")
            return self._get_empty_log_summary()
    
    def _calculate_log_trends(self, logs: List[LogEntry], hours: int) -> Dict[str, Any]:
        """Calculate log trends over time"""
        try:
            if not logs:
                return {}
            
            # Group logs by hour
            hourly_stats = {}
            for log in logs:
                hour_key = log.timestamp.replace(minute=0, second=0, microsecond=0)
                if hour_key not in hourly_stats:
                    hourly_stats[hour_key] = {'total': 0, 'error': 0, 'warning': 0}
                
                hourly_stats[hour_key]['total'] += 1
                if log.level == 'error':
                    hourly_stats[hour_key]['error'] += 1
                elif log.level == 'warning':
                    hourly_stats[hour_key]['warning'] += 1
            
            # Convert to sorted list
            trend_data = []
            for hour, stats in sorted(hourly_stats.items()):
                trend_data.append({
                    'hour': hour.isoformat(),
                    'total': stats['total'],
                    'error': stats['error'],
                    'warning': stats['warning']
                })
            
            return {
                'hourly_trends': trend_data,
                'total_periods': len(trend_data),
                'avg_logs_per_hour': sum(s['total'] for s in hourly_stats.values()) / len(hourly_stats) if hourly_stats else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate log trends: {e}")
            return {}
    
    def _get_empty_log_summary(self) -> LogSummary:
        """Return empty log summary"""
        return LogSummary(
            total_entries=0,
            error_count=0,
            warning_count=0,
            info_count=0,
            debug_count=0,
            time_range=(datetime.now(), datetime.now()),
            services=[],
            users=[]
        )
    
    def _get_empty_trends(self) -> Dict[str, Any]:
        """Return empty trends data"""
        return {
            'hourly_trends': [],
            'total_periods': 0,
            'avg_logs_per_hour': 0
        }
    
    def _get_error_log_summary(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Return error log summary"""
        return {
            'user_id': user_id,
            'org_id': org_id,
            'error': 'Failed to retrieve log summary',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_error_trends(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Return error trends data"""
        return {
            'user_id': user_id,
            'org_id': org_id,
            'error': 'Failed to retrieve log trends',
            'timestamp': datetime.now().isoformat()
        }
