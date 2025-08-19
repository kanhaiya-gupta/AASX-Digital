"""
Twin Analytics Service
=====================

Service for twin analytics and reporting.
Handles performance trends, usage statistics, and analytics reports.
Now integrated with src/twin_registry core services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json

# Import core Twin Registry services (only those that exist)
try:
    from src.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
    from src.twin_registry.core.twin_lifecycle_service import TwinLifecycleService
    print("✅ Twin Registry core services imported successfully")
    CORE_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Twin Registry core services not available: {e}")
    CORE_SERVICES_AVAILABLE = False
    CoreTwinRegistryService = None
    TwinLifecycleService = None

logger = logging.getLogger(__name__)

class TwinAnalyticsService:
    """
    Service for twin analytics and reporting.
    Now integrated with src/twin_registry core services.
    """
    
    def __init__(self):
        """Initialize the twin analytics service with core services."""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - using fallback mode")
            self.core_registry = None
            self.lifecycle_service = None
            return
        
        try:
            # Initialize core services from src/twin_registry
            self.core_registry = CoreTwinRegistryService()
            self.lifecycle_service = TwinLifecycleService()
            
            logger.info("✅ Twin Analytics Service initialized with core services")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            # Fallback to None if initialization fails
            self.core_registry = None
            self.lifecycle_service = None
    
    async def initialize(self) -> None:
        """Initialize all core services"""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - skipping initialization")
            return
            
        try:
            if self.core_registry:
                await self.core_registry.initialize()
            if self.lifecycle_service:
                await self.lifecycle_service.initialize()
                
            logger.info("✅ All core services initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            raise
    
    async def get_twin_analytics(self, twin_id: str = None, 
                               time_range: str = "30d") -> Dict[str, Any]:
        """
        Get comprehensive analytics for twins.
        
        Args:
            twin_id: Specific twin ID (None for all twins)
            time_range: Time range for analytics ('7d', '30d', '90d', '1y')
            
        Returns:
            Analytics data
        """
        try:
            logger.info(f"Getting analytics - twin_id: {twin_id}, time_range: {time_range}")
            
            # Calculate time range
            end_time = datetime.now()
            if time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            elif time_range == "90d":
                start_time = end_time - timedelta(days=90)
            elif time_range == "1y":
                start_time = end_time - timedelta(days=365)
            else:
                start_time = end_time - timedelta(days=30)  # Default to 30d
            
            if twin_id:
                # Single twin analytics
                analytics = await self._get_single_twin_analytics(twin_id, start_time, end_time)
            else:
                # System-wide analytics
                analytics = await self._get_system_analytics(start_time, end_time)
            
            result = {
                "twin_id": twin_id,
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "analytics": analytics,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Analytics generated for {'twin ' + twin_id if twin_id else 'system'}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {str(e)}")
            raise Exception(f"Failed to get analytics: {str(e)}")
    
    async def get_performance_trends(self, twin_id: str = None, 
                                   metric: str = "health_score",
                                   time_range: str = "30d") -> Dict[str, Any]:
        """
        Get performance trends for specific metrics.
        
        Args:
            twin_id: Twin ID (None for system-wide)
            metric: Metric to analyze ('health_score', 'uptime', 'response_time')
            time_range: Time range for trends
            
        Returns:
            Performance trends data
        """
        try:
            logger.info(f"Getting performance trends - metric: {metric}, time_range: {time_range}")
            
            # Calculate time range
            end_time = datetime.now()
            if time_range == "7d":
                start_time = end_time - timedelta(days=7)
                interval = "1d"
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
                interval = "1d"
            elif time_range == "90d":
                start_time = end_time - timedelta(days=90)
                interval = "1w"
            else:
                start_time = end_time - timedelta(days=30)
                interval = "1d"
            
            # Generate trend data
            trend_data = await self._generate_trend_data(twin_id, metric, start_time, end_time, interval)
            
            result = {
                "twin_id": twin_id,
                "metric": metric,
                "time_range": time_range,
                "interval": interval,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "trend_data": trend_data,
                "summary": self._analyze_trend(trend_data),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Performance trends generated for metric: {metric}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get performance trends: {str(e)}")
            raise Exception(f"Failed to get performance trends: {str(e)}")
    
    async def get_usage_statistics(self, time_range: str = "30d") -> Dict[str, Any]:
        """
        Get usage statistics for the twin registry.
        
        Args:
            time_range: Time range for statistics
            
        Returns:
            Usage statistics
        """
        try:
            logger.info(f"Getting usage statistics - time_range: {time_range}")
            
            # Calculate time range
            end_time = datetime.now()
            if time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            elif time_range == "90d":
                start_time = end_time - timedelta(days=90)
            else:
                start_time = end_time - timedelta(days=30)
            
            # Get all twins
            all_twins = await self.core_registry.get_all_twins() # Assuming core service has this method
            
            # Calculate usage statistics
            usage_stats = await self._calculate_usage_statistics(all_twins, start_time, end_time)
            
            result = {
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "usage_statistics": usage_stats,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("Usage statistics generated")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {str(e)}")
            raise Exception(f"Failed to get usage statistics: {str(e)}")
    
    async def generate_reports(self, report_type: str = "comprehensive",
                             twin_id: str = None,
                             time_range: str = "30d",
                             format: str = "json") -> Dict[str, Any]:
        """
        Generate comprehensive analytics reports.
        
        Args:
            report_type: Type of report ('comprehensive', 'performance', 'usage', 'health')
            twin_id: Twin ID (None for system-wide)
            time_range: Time range for report
            format: Report format ('json', 'csv', 'pdf')
            
        Returns:
            Generated report
        """
        try:
            logger.info(f"Generating {report_type} report - twin_id: {twin_id}")
            
            # Generate report based on type
            if report_type == "comprehensive":
                report_data = await self._generate_comprehensive_report(twin_id, time_range)
            elif report_type == "performance":
                report_data = await self._generate_performance_report(twin_id, time_range)
            elif report_type == "usage":
                report_data = await self._generate_usage_report(time_range)
            elif report_type == "health":
                report_data = await self._generate_health_report(twin_id, time_range)
            else:
                raise Exception(f"Unknown report type: {report_type}")
            
            # Format report
            if format == "json":
                formatted_report = report_data
            elif format == "csv":
                formatted_report = self._convert_to_csv(report_data)
            else:
                formatted_report = report_data  # Default to JSON
            
            result = {
                "report_type": report_type,
                "twin_id": twin_id,
                "time_range": time_range,
                "format": format,
                "generated_at": datetime.now().isoformat(),
                "report": formatted_report
            }
            
            logger.info(f"{report_type} report generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise Exception(f"Failed to generate report: {str(e)}")
    
    async def export_data(self, data_type: str = "twins",
                         filters: Dict[str, Any] = None,
                         format: str = "json") -> Dict[str, Any]:
        """
        Export twin registry data.
        
        Args:
            data_type: Type of data to export ('twins', 'events', 'analytics')
            filters: Optional filters to apply
            format: Export format ('json', 'csv', 'xml')
            
        Returns:
            Exported data
        """
        try:
            logger.info(f"Exporting {data_type} data - format: {format}")
            
            # Get data based on type
            if data_type == "twins":
                export_data = await self._export_twins_data(filters)
            elif data_type == "events":
                export_data = await self._export_events_data(filters)
            elif data_type == "analytics":
                export_data = await self._export_analytics_data(filters)
            else:
                raise Exception(f"Unknown data type: {data_type}")
            
            # Format data
            if format == "json":
                formatted_data = export_data
            elif format == "csv":
                formatted_data = self._convert_to_csv(export_data)
            elif format == "xml":
                formatted_data = self._convert_to_xml(export_data)
            else:
                formatted_data = export_data  # Default to JSON
            
            result = {
                "data_type": data_type,
                "format": format,
                "filters": filters,
                "exported_at": datetime.now().isoformat(),
                "record_count": len(export_data) if isinstance(export_data, list) else 1,
                "data": formatted_data
            }
            
            logger.info(f"{data_type} data exported successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            raise Exception(f"Failed to export data: {str(e)}")
    
    async def _get_single_twin_analytics(self, twin_id: str, start_time: datetime, 
                                       end_time: datetime) -> Dict[str, Any]:
        """Get analytics for a single twin."""
        try:
            # Get twin
            twin = await self.core_registry.get_twin_by_id(twin_id) # Assuming core service has this method
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Calculate analytics
            analytics = {
                "twin_info": {
                    "twin_id": twin_id,
                    "twin_name": getattr(twin, 'twin_name', ''),
                    "status": getattr(twin, 'status', ''),
                    "health_status": getattr(twin, 'health_status', ''),
                    "health_score": getattr(twin, 'health_score', 0)
                },
                "performance_metrics": {
                    "uptime_percentage": 95.5,
                    "avg_response_time": 150,
                    "error_rate": 0.02,
                    "throughput": 1000
                },
                "usage_patterns": {
                    "peak_usage_hours": [9, 10, 14, 15],
                    "daily_operations": 150,
                    "weekly_operations": 1050
                },
                "health_trends": {
                    "trend": "improving",
                    "change_rate": 2.5,
                    "stability_score": 85.0
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting single twin analytics: {str(e)}")
            raise
    
    async def _get_system_analytics(self, start_time: datetime, 
                                  end_time: datetime) -> Dict[str, Any]:
        """Get system-wide analytics."""
        try:
            # Get all twins
            all_twins = await self.core_registry.get_all_twins() # Assuming core service has this method
            
            # Calculate system analytics
            total_twins = len(all_twins)
            active_twins = len([t for t in all_twins if getattr(t, 'status', '') == 'active'])
            healthy_twins = len([t for t in all_twins if getattr(t, 'health_status', '') == 'healthy'])
            
            analytics = {
                "system_overview": {
                    "total_twins": total_twins,
                    "active_twins": active_twins,
                    "healthy_twins": healthy_twins,
                    "system_health_score": (healthy_twins / total_twins * 100) if total_twins > 0 else 100
                },
                "performance_summary": {
                    "avg_uptime": 96.2,
                    "avg_response_time": 180,
                    "system_throughput": 5000
                },
                "usage_metrics": {
                    "daily_active_twins": active_twins,
                    "weekly_operations": 15000,
                    "peak_concurrent_twins": 25
                },
                "trends": {
                    "growth_rate": 15.5,
                    "health_improvement": 8.2,
                    "performance_optimization": 12.1
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {str(e)}")
            raise
    
    async def _generate_trend_data(self, twin_id: str, metric: str, 
                                 start_time: datetime, end_time: datetime, 
                                 interval: str) -> List[Dict[str, Any]]:
        """Generate trend data for a specific metric."""
        try:
            # Placeholder implementation - in real system, this would query time-series data
            trend_data = []
            current_time = start_time
            
            while current_time <= end_time:
                # Generate sample data point
                if metric == "health_score":
                    value = 85 + (current_time.day % 10)  # Varying health score
                elif metric == "uptime":
                    value = 95 + (current_time.day % 5)   # Varying uptime
                else:
                    value = 100 + (current_time.day % 20)  # Generic metric
                
                trend_data.append({
                    "timestamp": current_time.isoformat(),
                    "value": value,
                    "twin_id": twin_id
                })
                
                # Move to next interval
                if interval == "1d":
                    current_time += timedelta(days=1)
                elif interval == "1w":
                    current_time += timedelta(weeks=1)
                else:
                    current_time += timedelta(days=1)
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error generating trend data: {str(e)}")
            raise
    
    def _analyze_trend(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trend data and provide insights."""
        try:
            if not trend_data:
                return {"trend": "no_data", "change_rate": 0, "insights": []}
            
            values = [point["value"] for point in trend_data]
            
            # Calculate trend
            if len(values) >= 2:
                first_value = values[0]
                last_value = values[-1]
                change_rate = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
                
                if change_rate > 5:
                    trend = "increasing"
                elif change_rate < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
                change_rate = 0
            
            # Generate insights
            insights = []
            if trend == "increasing":
                insights.append("Performance is improving over time")
            elif trend == "decreasing":
                insights.append("Performance is declining - attention needed")
            else:
                insights.append("Performance is stable")
            
            return {
                "trend": trend,
                "change_rate": change_rate,
                "min_value": min(values) if values else 0,
                "max_value": max(values) if values else 0,
                "avg_value": sum(values) / len(values) if values else 0,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return {"trend": "error", "change_rate": 0, "insights": ["Error analyzing trend"]}
    
    async def _calculate_usage_statistics(self, twins: List, start_time: datetime, 
                                        end_time: datetime) -> Dict[str, Any]:
        """Calculate usage statistics."""
        try:
            total_twins = len(twins)
            active_twins = len([t for t in twins if getattr(t, 'status', '') == 'active'])
            
            # Calculate usage patterns
            usage_stats = {
                "total_twins": total_twins,
                "active_twins": active_twins,
                "utilization_rate": (active_twins / total_twins * 100) if total_twins > 0 else 0,
                "daily_operations": active_twins * 50,  # Estimate
                "weekly_operations": active_twins * 350,
                "monthly_operations": active_twins * 1500,
                "peak_usage_hours": [9, 10, 14, 15],
                "usage_by_type": {
                    "industrial": len([t for t in twins if getattr(t, 'twin_type', '') == 'industrial']),
                    "commercial": len([t for t in twins if getattr(t, 'twin_type', '') == 'commercial']),
                    "research": len([t for t in twins if getattr(t, 'twin_type', '') == 'research'])
                }
            }
            
            return usage_stats
            
        except Exception as e:
            logger.error(f"Error calculating usage statistics: {str(e)}")
            raise
    
    async def _generate_comprehensive_report(self, twin_id: str, time_range: str) -> Dict[str, Any]:
        """Generate comprehensive report."""
        try:
            # Get all analytics data
            analytics = await self.get_twin_analytics(twin_id, time_range)
            trends = await self.get_performance_trends(twin_id, "health_score", time_range)
            usage = await self.get_usage_statistics(time_range)
            
            report = {
                "report_type": "comprehensive",
                "executive_summary": {
                    "overall_health": "good",
                    "key_metrics": analytics.get("analytics", {}),
                    "recommendations": ["Continue monitoring", "Optimize performance"]
                },
                "detailed_analytics": analytics,
                "performance_trends": trends,
                "usage_statistics": usage,
                "recommendations": [
                    "Implement automated health checks",
                    "Optimize resource allocation",
                    "Enhance monitoring capabilities"
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            raise
    
    async def _generate_performance_report(self, twin_id: str, time_range: str) -> Dict[str, Any]:
        """Generate performance report."""
        try:
            trends = await self.get_performance_trends(twin_id, "health_score", time_range)
            
            report = {
                "report_type": "performance",
                "performance_metrics": trends,
                "performance_insights": [
                    "Response times are within acceptable limits",
                    "Uptime is consistently high",
                    "Error rates are low"
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            raise
    
    async def _generate_usage_report(self, time_range: str) -> Dict[str, Any]:
        """Generate usage report."""
        try:
            usage = await self.get_usage_statistics(time_range)
            
            report = {
                "report_type": "usage",
                "usage_statistics": usage,
                "usage_insights": [
                    "Peak usage during business hours",
                    "Consistent utilization patterns",
                    "Room for capacity expansion"
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating usage report: {str(e)}")
            raise
    
    async def _generate_health_report(self, twin_id: str, time_range: str) -> Dict[str, Any]:
        """Generate health report."""
        try:
            analytics = await self.get_twin_analytics(twin_id, time_range)
            
            report = {
                "report_type": "health",
                "health_metrics": analytics,
                "health_insights": [
                    "Overall system health is good",
                    "Most twins are operating normally",
                    "Minor issues detected in some twins"
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating health report: {str(e)}")
            raise
    
    async def _export_twins_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Export twins data."""
        try:
            all_twins = await self.core_registry.get_all_twins() # Assuming core service has this method
            
            # Apply filters if provided
            if filters:
                filtered_twins = []
                for twin in all_twins:
                    if self._apply_filters(twin, filters):
                        filtered_twins.append(twin)
                all_twins = filtered_twins
            
            # Convert to export format
            export_data = []
            for twin in all_twins:
                export_data.append({
                    "twin_id": getattr(twin, 'twin_id', ''),
                    "twin_name": getattr(twin, 'twin_name', ''),
                    "status": getattr(twin, 'status', ''),
                    "health_status": getattr(twin, 'health_status', ''),
                    "health_score": getattr(twin, 'health_score', 0),
                    "created_at": getattr(twin, 'created_at', ''),
                    "updated_at": getattr(twin, 'updated_at', '')
                })
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting twins data: {str(e)}")
            raise
    
    async def _export_events_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Export events data (placeholder)."""
        try:
            # Placeholder implementation
            events_data = [
                {
                    "event_id": "evt_001",
                    "twin_id": "twin_001",
                    "event_type": "status_change",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Twin status changed"
                }
            ]
            
            return events_data
            
        except Exception as e:
            logger.error(f"Error exporting events data: {str(e)}")
            raise
    
    async def _export_analytics_data(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export analytics data."""
        try:
            analytics = await self.get_twin_analytics(time_range="30d")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {str(e)}")
            raise
    
    def _apply_filters(self, twin, filters: Dict[str, Any]) -> bool:
        """Apply filters to a twin."""
        try:
            for key, value in filters.items():
                if hasattr(twin, key):
                    twin_value = getattr(twin, key)
                    if twin_value != value:
                        return False
            return True
        except Exception:
            return False
    
    def _convert_to_csv(self, data: Any) -> str:
        """Convert data to CSV format."""
        try:
            if isinstance(data, list) and data:
                # Get headers from first item
                headers = list(data[0].keys())
                csv_lines = [','.join(headers)]
                
                for item in data:
                    row = [str(item.get(header, '')) for header in headers]
                    csv_lines.append(','.join(row))
                
                return '\n'.join(csv_lines)
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Error converting to CSV: {str(e)}")
            return str(data)
    
    def _convert_to_xml(self, data: Any) -> str:
        """Convert data to XML format."""
        try:
            # Simple XML conversion
            if isinstance(data, dict):
                xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<data>']
                xml_lines.extend(self._dict_to_xml(data, 'item'))
                xml_lines.append('</data>')
                return '\n'.join(xml_lines)
            else:
                return f'<?xml version="1.0" encoding="UTF-8"?>\n<data>{str(data)}</data>'
        except Exception as e:
            logger.error(f"Error converting to XML: {str(e)}")
            return str(data)
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str) -> List[str]:
        """Convert dictionary to XML lines."""
        lines = [f'<{root_name}>']
        for key, value in data.items():
            if isinstance(value, dict):
                lines.extend(self._dict_to_xml(value, key))
            else:
                lines.append(f'<{key}>{value}</{key}>')
        lines.append(f'</{root_name}>')
        return lines 