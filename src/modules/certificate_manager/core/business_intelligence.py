"""
Business Intelligence - Business Insights and Analytics Service

Handles business insights generation, analytics, and reporting
for certificates. Provides comprehensive business intelligence,
trend analysis, and actionable insights for decision-making.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from collections import defaultdict

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    CertificateStatus,
    QualityLevel
)
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_metrics_service import CertificatesMetricsService

logger = logging.getLogger(__name__)


class InsightType(str, Enum):
    """Types of business insights"""
    PERFORMANCE_TREND = "performance_trend"
    QUALITY_ANALYSIS = "quality_analysis"
    COMPLIANCE_OVERVIEW = "compliance_overview"
    SECURITY_INSIGHTS = "security_insights"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    BUSINESS_IMPACT = "business_impact"


class ReportFormat(str, Enum):
    """Report output formats"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    MARKDOWN = "markdown"


class BusinessIntelligence:
    """
    Business intelligence and analytics service
    
    Handles:
    - Business insights generation
    - Trend analysis and forecasting
    - Performance analytics
    - Compliance reporting
    - Security insights
    - Operational efficiency metrics
    """
    
    def __init__(
        self,
        registry_service: CertificatesRegistryService,
        metrics_service: CertificatesMetricsService
    ):
        """Initialize the business intelligence service"""
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Insight cache
        self.insight_cache: Dict[str, Dict[str, Any]] = {}
        
        # Report generation locks
        self.report_locks: Dict[str, asyncio.Lock] = {}
        
        # Analytics history
        self.analytics_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Business metrics thresholds
        self.business_thresholds = {
            "quality_target": 85.0,
            "compliance_target": 95.0,
            "security_target": 80.0,
            "efficiency_target": 90.0,
            "completion_target": 95.0
        }
        
        logger.info("Business Intelligence service initialized successfully")
    
    async def generate_business_insights(
        self,
        certificate_id: Optional[str] = None,
        insight_types: Optional[List[InsightType]] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive business insights
        
        This is the main entry point for business intelligence.
        Generates insights based on specified types and time range.
        """
        try:
            logger.info(f"Generating business insights for {'all certificates' if certificate_id is None else certificate_id}")
            
            # Default to all insight types if none specified
            if insight_types is None:
                insight_types = list(InsightType)
            
            # Generate insights for each type
            insights = {}
            for insight_type in insight_types:
                if insight_type == InsightType.PERFORMANCE_TREND:
                    insights[insight_type.value] = await self._generate_performance_trends(
                        certificate_id, time_range_days
                    )
                elif insight_type == InsightType.QUALITY_ANALYSIS:
                    insights[insight_type.value] = await self._generate_quality_analysis(
                        certificate_id, time_range_days
                    )
                elif insight_type == InsightType.COMPLIANCE_OVERVIEW:
                    insights[insight_type.value] = await self._generate_compliance_overview(
                        certificate_id, time_range_days
                    )
                elif insight_type == InsightType.SECURITY_INSIGHTS:
                    insights[insight_type.value] = await self._generate_security_insights(
                        certificate_id, time_range_days
                    )
                elif insight_type == InsightType.OPERATIONAL_EFFICIENCY:
                    insights[insight_type.value] = await self._generate_operational_efficiency(
                        certificate_id, time_range_days
                    )
                elif insight_type == InsightType.BUSINESS_IMPACT:
                    insights[insight_type.value] = await self._generate_business_impact(
                        certificate_id, time_range_days
                    )
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(insights)
            
            # Cache insights
            cache_key = f"{certificate_id or 'all'}_{time_range_days}"
            self.insight_cache[cache_key] = {
                "insights": insights,
                "executive_summary": executive_summary,
                "generated_at": datetime.utcnow().isoformat(),
                "time_range_days": time_range_days
            }
            
            # Record analytics history
            await self._record_analytics_history(cache_key, insights, executive_summary)
            
            logger.info(f"Successfully generated business insights for {len(insight_types)} types")
            
            return {
                "insights": insights,
                "executive_summary": executive_summary,
                "metadata": {
                    "certificate_id": certificate_id,
                    "time_range_days": time_range_days,
                    "insight_types": [t.value for t in insight_types],
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating business insights: {e}")
            return {}
    
    async def _generate_performance_trends(
        self,
        certificate_id: Optional[str],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Generate performance trend insights"""
        try:
            # Get performance metrics
            if certificate_id:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate_id, limit=1000
                )
            else:
                # Get metrics for all certificates
                metrics = await self.metrics_service.get_all_metrics(limit=1000)
            
            # Filter by time range
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            recent_metrics = [
                m for m in metrics 
                if m.recorded_at >= cutoff_date and 
                m.metric_category == MetricCategory.PERFORMANCE
            ]
            
            # Group by metric name and calculate trends
            metric_trends = {}
            for metric in recent_metrics:
                metric_name = metric.metric_name
                if metric_name not in metric_trends:
                    metric_trends[metric_name] = []
                metric_trends[metric_name].append({
                    "value": metric.metric_value,
                    "timestamp": metric.recorded_at,
                    "unit": metric.metric_unit
                })
            
            # Calculate trend analysis for each metric
            trend_analysis = {}
            for metric_name, data_points in metric_trends.items():
                if len(data_points) >= 2:
                    # Sort by timestamp
                    sorted_data = sorted(data_points, key=lambda x: x["timestamp"])
                    
                    # Calculate trend
                    first_value = sorted_data[0]["value"]
                    last_value = sorted_data[-1]["value"]
                    value_change = last_value - first_value
                    
                    # Calculate average rate of change
                    time_span = (sorted_data[-1]["timestamp"] - sorted_data[0]["timestamp"]).total_seconds() / 3600  # hours
                    rate_per_hour = value_change / time_span if time_span > 0 else 0
                    
                    trend_analysis[metric_name] = {
                        "trend": "improving" if value_change > 0 else "declining" if value_change < 0 else "stable",
                        "value_change": round(value_change, 4),
                        "rate_per_hour": round(rate_per_hour, 4),
                        "first_value": first_value,
                        "last_value": last_value,
                        "data_points": len(data_points),
                        "unit": sorted_data[0]["unit"]
                    }
            
            return {
                "metric_trends": trend_analysis,
                "total_metrics_analyzed": len(trend_analysis),
                "time_range_hours": time_range_days * 24,
                "data_points_analyzed": len(recent_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error generating performance trends: {e}")
            return {}
    
    async def _generate_quality_analysis(
        self,
        certificate_id: Optional[str],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Generate quality analysis insights"""
        try:
            # Get quality metrics
            if certificate_id:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate_id, limit=1000
                )
            else:
                metrics = await self.metrics_service.get_all_metrics(limit=1000)
            
            # Filter by time range and quality category
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            quality_metrics = [
                m for m in metrics 
                if m.recorded_at >= cutoff_date and 
                m.metric_category == MetricCategory.QUALITY
            ]
            
            # Analyze quality trends
            quality_trends = {}
            for metric in quality_metrics:
                metric_name = metric.metric_name
                if metric_name not in quality_trends:
                    quality_trends[metric_name] = []
                quality_trends[metric_name].append({
                    "value": metric.metric_value,
                    "timestamp": metric.recorded_at
                })
            
            # Calculate quality statistics
            quality_stats = {}
            for metric_name, data_points in quality_trends.items():
                values = [dp["value"] for dp in data_points]
                if values:
                    quality_stats[metric_name] = {
                        "current_value": values[-1],
                        "average_value": sum(values) / len(values),
                        "min_value": min(values),
                        "max_value": max(values),
                        "trend": "improving" if values[-1] > values[0] else "declining" if values[-1] < values[0] else "stable",
                        "data_points": len(values)
                    }
            
            # Calculate overall quality score
            overall_quality = 0.0
            if quality_stats:
                current_scores = [stats["current_value"] for stats in quality_stats.values()]
                overall_quality = sum(current_scores) / len(current_scores)
            
            # Quality recommendations
            recommendations = []
            if overall_quality < self.business_thresholds["quality_target"]:
                recommendations.append("Overall quality score below target - review quality processes")
            
            for metric_name, stats in quality_stats.items():
                if stats["current_value"] < 80.0:
                    recommendations.append(f"{metric_name} quality below threshold - investigate issues")
            
            return {
                "overall_quality_score": round(overall_quality, 2),
                "quality_target": self.business_thresholds["quality_target"],
                "quality_metrics": quality_stats,
                "recommendations": recommendations,
                "total_metrics_analyzed": len(quality_stats),
                "time_range_days": time_range_days
            }
            
        except Exception as e:
            logger.error(f"Error generating quality analysis: {e}")
            return {}
    
    async def _generate_compliance_overview(
        self,
        certificate_id: Optional[str],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Generate compliance overview insights"""
        try:
            # Get compliance metrics
            if certificate_id:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate_id, limit=1000
                )
            else:
                metrics = await self.metrics_service.get_all_metrics(limit=1000)
            
            # Filter by time range and compliance category
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            compliance_metrics = [
                m for m in metrics 
                if m.recorded_at >= cutoff_date and 
                m.metric_category == MetricCategory.COMPLIANCE
            ]
            
            # Analyze compliance status
            compliance_status = defaultdict(int)
            compliance_scores = []
            
            for metric in compliance_metrics:
                if "status" in metric.metric_name.lower():
                    compliance_status[metric.metric_value] += 1
                elif "score" in metric.metric_name.lower():
                    compliance_scores.append(metric.metric_value)
            
            # Calculate compliance statistics
            overall_compliance_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
            
            # Compliance recommendations
            recommendations = []
            if overall_compliance_score < self.business_thresholds["compliance_target"]:
                recommendations.append("Compliance score below target - review regulatory requirements")
            
            if compliance_status.get("non_compliant", 0) > 0:
                recommendations.append("Non-compliant items detected - immediate action required")
            
            return {
                "overall_compliance_score": round(overall_compliance_score, 2),
                "compliance_target": self.business_thresholds["compliance_target"],
                "compliance_status_distribution": dict(compliance_status),
                "compliance_scores": compliance_scores,
                "recommendations": recommendations,
                "total_metrics_analyzed": len(compliance_metrics),
                "time_range_days": time_range_days
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance overview: {e}")
            return {}
    
    async def _generate_security_insights(
        self,
        certificate_id: Optional[str],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Generate security insights"""
        try:
            # Get security metrics
            if certificate_id:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate_id, limit=1000
                )
            else:
                metrics = await self.metrics_service.get_all_metrics(limit=1000)
            
            # Filter by time range and security category
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            security_metrics = [
                m for m in metrics 
                if m.recorded_at >= cutoff_date and 
                m.metric_category == MetricCategory.SECURITY
            ]
            
            # Analyze security trends
            security_scores = []
            security_events = []
            
            for metric in security_metrics:
                if "score" in metric.metric_name.lower():
                    security_scores.append(metric.metric_value)
                elif "event" in metric.metric_name.lower():
                    security_events.append({
                        "name": metric.metric_name,
                        "value": metric.metric_value,
                        "timestamp": metric.recorded_at
                    })
            
            # Calculate security statistics
            overall_security_score = sum(security_scores) / len(security_scores) if security_scores else 0.0
            
            # Security recommendations
            recommendations = []
            if overall_security_score < self.business_thresholds["security_target"]:
                recommendations.append("Security score below target - review security measures")
            
            if len(security_events) > 10:
                recommendations.append("High number of security events - investigate potential threats")
            
            return {
                "overall_security_score": round(overall_security_score, 2),
                "security_target": self.business_thresholds["security_target"],
                "security_events_count": len(security_events),
                "security_events": security_events,
                "recommendations": recommendations,
                "total_metrics_analyzed": len(security_metrics),
                "time_range_days": time_range_days
            }
            
        except Exception as e:
            logger.error(f"Error generating security insights: {e}")
            return {}
    
    async def _generate_operational_efficiency(
        self,
        certificate_id: Optional[str],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Generate operational efficiency insights"""
        try:
            # Get performance and quality metrics
            if certificate_id:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate_id, limit=1000
                )
            else:
                metrics = await self.metrics_service.get_all_metrics(limit=1000)
            
            # Filter by time range
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            recent_metrics = [m for m in metrics if m.recorded_at >= cutoff_date]
            
            # Calculate efficiency metrics
            processing_times = []
            success_rates = []
            resource_utilization = []
            
            for metric in recent_metrics:
                if "time" in metric.metric_name.lower() or "duration" in metric.metric_name.lower():
                    processing_times.append(metric.metric_value)
                elif "success" in metric.metric_name.lower() or "completion" in metric.metric_name.lower():
                    success_rates.append(metric.metric_value)
                elif "utilization" in metric.metric_name.lower() or "efficiency" in metric.metric_name.lower():
                    resource_utilization.append(metric.metric_value)
            
            # Calculate efficiency statistics
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
            avg_resource_utilization = sum(resource_utilization) / len(resource_utilization) if resource_utilization else 0.0
            
            # Overall efficiency score
            efficiency_factors = []
            if processing_times:
                efficiency_factors.append(100.0 - min(avg_processing_time / 1000, 100.0))  # Normalize processing time
            if success_rates:
                efficiency_factors.append(avg_success_rate)
            if resource_utilization:
                efficiency_factors.append(avg_resource_utilization)
            
            overall_efficiency = sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.0
            
            # Efficiency recommendations
            recommendations = []
            if overall_efficiency < self.business_thresholds["efficiency_target"]:
                recommendations.append("Operational efficiency below target - optimize processes")
            
            if avg_processing_time > 5000:  # 5 seconds
                recommendations.append("High processing times detected - investigate bottlenecks")
            
            if avg_success_rate < 90.0:
                recommendations.append("Low success rates - review error handling")
            
            return {
                "overall_efficiency_score": round(overall_efficiency, 2),
                "efficiency_target": self.business_thresholds["efficiency_target"],
                "avg_processing_time_ms": round(avg_processing_time, 2),
                "avg_success_rate": round(avg_success_rate, 2),
                "avg_resource_utilization": round(avg_resource_utilization, 2),
                "recommendations": recommendations,
                "total_metrics_analyzed": len(recent_metrics),
                "time_range_days": time_range_days
            }
            
        except Exception as e:
            logger.error(f"Error generating operational efficiency: {e}")
            return {}
    
    async def _generate_business_impact(
        self,
        certificate_id: Optional[str],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Generate business impact insights"""
        try:
            # Get business metrics
            if certificate_id:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate_id, limit=1000
                )
            else:
                metrics = await self.metrics_service.get_all_metrics(limit=1000)
            
            # Filter by time range and business category
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            business_metrics = [
                m for m in metrics 
                if m.recorded_at >= cutoff_date and 
                m.metric_category == MetricCategory.BUSINESS
            ]
            
            # Analyze business impact
            business_scores = []
            stakeholder_metrics = []
            
            for metric in business_metrics:
                if "score" in metric.metric_name.lower():
                    business_scores.append(metric.metric_value)
                elif "stakeholder" in metric.metric_name.lower() or "business" in metric.metric_name.lower():
                    stakeholder_metrics.append({
                        "name": metric.metric_name,
                        "value": metric.metric_value,
                        "timestamp": metric.recorded_at
                    })
            
            # Calculate business impact statistics
            overall_business_score = sum(business_scores) / len(business_scores) if business_scores else 0.0
            
            # Business impact recommendations
            recommendations = []
            if overall_business_score < 80.0:
                recommendations.append("Business impact score below target - review business value")
            
            if len(stakeholder_metrics) < 5:
                recommendations.append("Limited stakeholder metrics - expand business monitoring")
            
            return {
                "overall_business_score": round(overall_business_score, 2),
                "stakeholder_metrics": stakeholder_metrics,
                "recommendations": recommendations,
                "total_metrics_analyzed": len(business_metrics),
                "time_range_days": time_range_days
            }
            
        except Exception as e:
            logger.error(f"Error generating business impact: {e}")
            return {}
    
    async def _generate_executive_summary(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of all insights"""
        try:
            summary = {
                "overview": "Business Intelligence Summary",
                "generated_at": datetime.utcnow().isoformat(),
                "key_metrics": {},
                "critical_issues": [],
                "recommendations": [],
                "overall_health": "healthy"
            }
            
            # Extract key metrics
            if "quality_analysis" in insights:
                quality = insights["quality_analysis"]
                summary["key_metrics"]["overall_quality"] = quality.get("overall_quality_score", 0)
                summary["recommendations"].extend(quality.get("recommendations", []))
            
            if "compliance_overview" in insights:
                compliance = insights["compliance_overview"]
                summary["key_metrics"]["compliance_score"] = compliance.get("overall_compliance_score", 0)
                summary["recommendations"].extend(compliance.get("recommendations", []))
            
            if "security_insights" in insights:
                security = insights["security_insights"]
                summary["key_metrics"]["security_score"] = security.get("overall_security_score", 0)
                summary["recommendations"].extend(security.get("recommendations", []))
            
            if "operational_efficiency" in insights:
                efficiency = insights["operational_efficiency"]
                summary["key_metrics"]["efficiency_score"] = efficiency.get("overall_efficiency_score", 0)
                summary["recommendations"].extend(efficiency.get("recommendations", []))
            
            # Determine overall health
            critical_issues = [rec for rec in summary["recommendations"] if "immediate action" in rec.lower() or "critical" in rec.lower()]
            if critical_issues:
                summary["overall_health"] = "critical"
                summary["critical_issues"] = critical_issues
            elif len(summary["recommendations"]) > 5:
                summary["overall_health"] = "warning"
            else:
                summary["overall_health"] = "healthy"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return {}
    
    async def _record_analytics_history(
        self,
        cache_key: str,
        insights: Dict[str, Any],
        executive_summary: Dict[str, Any]
    ) -> None:
        """Record analytics generation history"""
        try:
            if cache_key not in self.analytics_history:
                self.analytics_history[cache_key] = []
            
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "insights_generated": len(insights),
                "overall_health": executive_summary.get("overall_health", "unknown"),
                "critical_issues_count": len(executive_summary.get("critical_issues", [])),
                "recommendations_count": len(executive_summary.get("recommendations", [])),
                "cache_key": cache_key
            }
            
            self.analytics_history[cache_key].append(history_entry)
            
            # Keep only last 10 entries
            if len(self.analytics_history[cache_key]) > 10:
                self.analytics_history[cache_key] = self.analytics_history[cache_key][-10:]
                
        except Exception as e:
            logger.error(f"Error recording analytics history: {e}")
    
    async def generate_report(
        self,
        report_type: str = "comprehensive",
        format: ReportFormat = ReportFormat.JSON,
        certificate_id: Optional[str] = None,
        time_range_days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Generate formatted business intelligence report"""
        try:
            # Generate insights
            insights = await self.generate_business_insights(
                certificate_id=certificate_id,
                time_range_days=time_range_days
            )
            
            if not insights:
                return None
            
            # Format report based on requested format
            if format == ReportFormat.JSON:
                return insights
            elif format == ReportFormat.HTML:
                return await self._format_as_html(insights)
            elif format == ReportFormat.MARKDOWN:
                return await self._format_as_markdown(insights)
            elif format == ReportFormat.CSV:
                return await self._format_as_csv(insights)
            else:
                return insights
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    async def _format_as_html(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Format insights as HTML report"""
        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Business Intelligence Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 20px; }
                    .section { margin: 20px 0; padding: 15px; border: 1px solid #ecf0f1; }
                    .section-title { color: #2c3e50; font-weight: bold; margin-bottom: 10px; }
                    .metric { display: inline-block; margin: 5px 10px; }
                    .critical { color: #e74c3c; }
                    .warning { color: #f39c12; }
                    .healthy { color: #27ae60; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Business Intelligence Report</h1>
                    <p>Generated: {timestamp}</p>
                </div>
            """.format(timestamp=insights.get("metadata", {}).get("generated_at", "N/A"))
            
            # Add executive summary
            if "executive_summary" in insights:
                summary = insights["executive_summary"]
                health_class = summary.get("overall_health", "unknown")
                html_content += f'<div class="section"><div class="section-title">Executive Summary</div>'
                html_content += f'<div class="metric {health_class}">Overall Health: {health_class.upper()}</div>'
                html_content += f'<div class="metric">Key Metrics: {len(summary.get("key_metrics", {}))}</div>'
                html_content += f'<div class="metric">Recommendations: {len(summary.get("recommendations", []))}</div></div>'
            
            # Add insights sections
            for insight_type, insight_data in insights.get("insights", {}).items():
                if insight_data:
                    html_content += f'<div class="section"><div class="section-title">{insight_type.replace("_", " ").title()}</div>'
                    
                    for key, value in insight_data.items():
                        if isinstance(value, (int, float)):
                            html_content += f'<div class="metric">{key.replace("_", " ").title()}: {value}</div>'
                        elif isinstance(value, list):
                            html_content += f'<div class="metric">{key.replace("_", " ").title()}: {len(value)} items</div>'
                        else:
                            html_content += f'<div class="metric">{key.replace("_", " ").title()}: {value}</div>'
                    
                    html_content += '</div>'
            
            html_content += "</body></html>"
            
            return {
                "format": "html",
                "content": html_content,
                "metadata": insights.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error formatting as HTML: {e}")
            return {}
    
    async def _format_as_markdown(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Format insights as Markdown report"""
        try:
            markdown_content = "# Business Intelligence Report\n\n"
            markdown_content += f"**Generated:** {insights.get('metadata', {}).get('generated_at', 'N/A')}\n\n"
            
            # Add executive summary
            if "executive_summary" in insights:
                summary = insights["executive_summary"]
                markdown_content += "## Executive Summary\n\n"
                markdown_content += f"- **Overall Health:** {summary.get('overall_health', 'unknown')}\n"
                markdown_content += f"- **Key Metrics:** {len(summary.get('key_metrics', {}))}\n"
                markdown_content += f"- **Recommendations:** {len(summary.get('recommendations', []))}\n\n"
            
            # Add insights sections
            for insight_type, insight_data in insights.get("insights", {}).items():
                if insight_data:
                    markdown_content += f"## {insight_type.replace('_', ' ').title()}\n\n"
                    
                    for key, value in insight_data.items():
                        if isinstance(value, (int, float)):
                            markdown_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                        elif isinstance(value, list):
                            markdown_content += f"- **{key.replace('_', ' ').title()}:** {len(value)} items\n"
                        else:
                            markdown_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                    
                    markdown_content += "\n"
            
            return {
                "format": "markdown",
                "content": markdown_content,
                "metadata": insights.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error formatting as Markdown: {e}")
            return {}
    
    async def _format_as_csv(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Format insights as CSV report"""
        try:
            csv_content = "Metric,Value,Category\n"
            
            # Add executive summary
            if "executive_summary" in insights:
                summary = insights["executive_summary"]
                csv_content += f"Overall Health,{summary.get('overall_health', 'unknown')},Executive Summary\n"
                csv_content += f"Key Metrics Count,{len(summary.get('key_metrics', {}))},Executive Summary\n"
                csv_content += f"Recommendations Count,{len(summary.get('recommendations', []))},Executive Summary\n"
            
            # Add insights data
            for insight_type, insight_data in insights.get("insights", {}).items():
                for key, value in insight_data.items():
                    if isinstance(value, (int, float, str)):
                        csv_content += f"{key},{value},{insight_type}\n"
            
            return {
                "format": "csv",
                "content": csv_content,
                "metadata": insights.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error formatting as CSV: {e}")
            return {}
    
    async def get_cached_insights(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached business insights"""
        try:
            return self.insight_cache.get(cache_key)
        except Exception as e:
            logger.error(f"Error getting cached insights: {e}")
            return None
    
    async def get_analytics_history(self, cache_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get analytics generation history"""
        try:
            return self.analytics_history.get(cache_key, [])[-limit:]
        except Exception as e:
            logger.error(f"Error getting analytics history: {e}")
            return []
    
    async def update_business_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Update business metric thresholds"""
        try:
            for key, value in thresholds.items():
                if key in self.business_thresholds:
                    self.business_thresholds[key] = value
            
            logger.info(f"Updated business thresholds: {thresholds}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating business thresholds: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the business intelligence service"""
        try:
            health_status = {
                "status": "healthy",
                "insight_cache_size": len(self.insight_cache),
                "analytics_history_size": sum(len(h) for h in self.analytics_history.values()),
                "business_thresholds": self.business_thresholds,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
