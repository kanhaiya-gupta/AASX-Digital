"""
Performance Analytics Service
============================

Service for performance optimization and analytics in federated learning.
Uses pure async patterns for optimal performance.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService
from ..models.federated_learning_registry import FederatedLearningRegistry
from ..models.federated_learning_metrics import FederatedLearningMetrics
from ..repositories.federated_learning_registry_repository import FederatedLearningRegistryRepository
from ..repositories.federated_learning_metrics_repository import FederatedLearningMetricsRepository


class PerformanceAnalyticsService:
    """Service for performance optimization and analytics in federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize service with dependencies"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Initialize repositories
        self.registry_repo = FederatedLearningRegistryRepository(connection_manager)
        self.metrics_repo = FederatedLearningMetricsRepository(connection_manager)
    
    async def analyze_performance_trends(
        self,
        registry_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Analyze performance trends over time (async)"""
        try:
            # Get metrics within time range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics_list = await self.metrics_repo.get_by_time_range(
                registry_id, start_time, end_time
            )
            
            if not metrics_list:
                return {'error': 'No metrics data available for analysis'}
            
            # Calculate trends for key metrics
            trends = {
                'health_score': self._calculate_trend([m.health_score for m in metrics_list]),
                'response_time': self._calculate_trend([m.response_time_ms for m in metrics_list]),
                'uptime': self._calculate_trend([m.uptime_percentage for m in metrics_list]),
                'error_rate': self._calculate_trend([m.error_rate for m in metrics_list]),
                'cpu_usage': self._calculate_trend([m.cpu_usage_percent for m in metrics_list]),
                'memory_usage': self._calculate_trend([m.memory_usage_percent for m in metrics_list]),
                'federation_speed': self._calculate_trend([m.federation_participation_speed_sec for m in metrics_list]),
                'aggregation_speed': self._calculate_trend([m.aggregation_speed_sec for m in metrics_list])
            }
            
            # Identify performance patterns
            patterns = await self._identify_performance_patterns(metrics_list)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(trends, patterns)
            
            return {
                'registry_id': registry_id,
                'analysis_period_days': days,
                'trends': trends,
                'patterns': patterns,
                'recommendations': recommendations,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to analyze performance trends: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend for a list of values"""
        if not values or len(values) < 2:
            return {'trend': 'insufficient_data', 'change_percent': 0.0}
        
        # Calculate change percentage
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            change_percent = 100.0 if last_value > 0 else 0.0
        else:
            change_percent = ((last_value - first_value) / first_value) * 100
        
        # Determine trend direction
        if change_percent > 5.0:
            trend = 'improving'
        elif change_percent < -5.0:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percent': round(change_percent, 2),
            'first_value': first_value,
            'last_value': last_value,
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values)
        }
    
    async def _identify_performance_patterns(
        self,
        metrics_list: List[FederatedLearningMetrics]
    ) -> Dict[str, Any]:
        """Identify performance patterns in metrics data"""
        patterns = {
            'peak_hours': [],
            'bottlenecks': [],
            'anomalies': [],
            'correlations': {}
        }
        
        try:
            # Analyze peak hours
            hourly_metrics = {}
            for metrics in metrics_list:
                hour = metrics.created_at.hour
                if hour not in hourly_metrics:
                    hourly_metrics[hour] = []
                hourly_metrics[hour].append(metrics.health_score)
            
            # Find peak performance hours
            for hour, scores in hourly_metrics.items():
                avg_score = sum(scores) / len(scores)
                if avg_score > 85.0:
                    patterns['peak_hours'].append({
                        'hour': hour,
                        'avg_health_score': round(avg_score, 2)
                    })
            
            # Identify bottlenecks
            bottlenecks = []
            for metrics in metrics_list:
                if metrics.cpu_usage_percent > 90.0:
                    bottlenecks.append({
                        'timestamp': metrics.created_at.isoformat(),
                        'type': 'high_cpu_usage',
                        'value': metrics.cpu_usage_percent
                    })
                
                if metrics.memory_usage_percent > 90.0:
                    bottlenecks.append({
                        'timestamp': metrics.created_at.isoformat(),
                        'type': 'high_memory_usage',
                        'value': metrics.memory_usage_percent
                    })
                
                if metrics.response_time_ms > 1000.0:
                    bottlenecks.append({
                        'timestamp': metrics.created_at.isoformat(),
                        'type': 'slow_response_time',
                        'value': metrics.response_time_ms
                    })
            
            patterns['bottlenecks'] = bottlenecks
            
            # Detect anomalies
            anomalies = []
            health_scores = [m.health_score for m in metrics_list]
            if health_scores:
                avg_health = sum(health_scores) / len(health_scores)
                std_dev = (sum((x - avg_health) ** 2 for x in health_scores) / len(health_scores)) ** 0.5
                
                for metrics in metrics_list:
                    if abs(metrics.health_score - avg_health) > 2 * std_dev:
                        anomalies.append({
                            'timestamp': metrics.created_at.isoformat(),
                            'type': 'health_score_anomaly',
                            'value': metrics.health_score,
                            'expected_range': f"{avg_health - 2*std_dev:.1f} - {avg_health + 2*std_dev:.1f}"
                        })
            
            patterns['anomalies'] = anomalies
            
            # Analyze correlations
            if len(metrics_list) > 1:
                cpu_scores = [m.cpu_usage_percent for m in metrics_list]
                memory_scores = [m.memory_usage_percent for m in metrics_list]
                health_scores = [m.health_score for m in metrics_list]
                
                patterns['correlations'] = {
                    'cpu_health_correlation': self._calculate_correlation(cpu_scores, health_scores),
                    'memory_health_correlation': self._calculate_correlation(memory_scores, health_scores),
                    'response_time_health_correlation': self._calculate_correlation(
                        [m.response_time_ms for m in metrics_list], health_scores
                    )
                }
            
        except Exception as e:
            print(f"⚠️  Failed to identify patterns: {e}")
        
        return patterns
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        try:
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            sum_y2 = sum(y * y for y in y_values)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return round(correlation, 3)
            
        except Exception:
            return 0.0
    
    async def _generate_optimization_recommendations(
        self,
        trends: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        # Health score recommendations
        if trends.get('health_score', {}).get('trend') == 'declining':
            recommendations.append("Investigate declining health score trend")
            recommendations.append("Review recent system changes and deployments")
        
        # Response time recommendations
        if trends.get('response_time', {}).get('trend') == 'declining':
            recommendations.append("Optimize response time performance")
            recommendations.append("Consider caching strategies and query optimization")
        
        # Resource usage recommendations
        if trends.get('cpu_usage', {}).get('avg_value', 0) > 80.0:
            recommendations.append("High CPU usage detected - consider scaling or optimization")
        
        if trends.get('memory_usage', {}).get('avg_value', 0) > 80.0:
            recommendations.append("High memory usage detected - review memory management")
        
        # Bottleneck recommendations
        if patterns.get('bottlenecks'):
            recommendations.append("Performance bottlenecks detected - investigate resource constraints")
            recommendations.append("Consider horizontal scaling for high-traffic periods")
        
        # Anomaly recommendations
        if patterns.get('anomalies'):
            recommendations.append("Performance anomalies detected - implement monitoring alerts")
            recommendations.append("Review system logs for unusual activity")
        
        # Peak hours recommendations
        if patterns.get('peak_hours'):
            recommendations.append("Peak performance hours identified - optimize scheduling")
            recommendations.append("Consider load balancing during peak periods")
        
        # Federation speed recommendations
        if trends.get('federation_speed', {}).get('trend') == 'declining':
            recommendations.append("Federation participation speed declining - review network configuration")
            recommendations.append("Optimize data transmission protocols")
        
        # Aggregation speed recommendations
        if trends.get('aggregation_speed', {}).get('trend') == 'declining':
            recommendations.append("Model aggregation speed declining - review aggregation algorithms")
            recommendations.append("Consider parallel processing for aggregation")
        
        return recommendations
    
    async def get_performance_summary(
        self,
        registry_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive performance summary (async)"""
        try:
            # Get latest metrics
            latest_metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            if not latest_metrics:
                return {'error': 'No metrics data available'}
            
            # Get performance trends
            trends = await self.analyze_performance_trends(registry_id, days=7)
            
            # Calculate performance score
            performance_score = await latest_metrics.calculate_overall_performance_score()
            
            # Get resource utilization summary
            resource_summary = await latest_metrics.get_resource_utilization_summary()
            
            # Get federation performance summary
            federation_summary = await latest_metrics.get_federation_performance_summary()
            
            return {
                'registry_id': registry_id,
                'summary_date': datetime.now().isoformat(),
                'overall_performance_score': performance_score,
                'current_metrics': {
                    'health_score': latest_metrics.health_score,
                    'response_time_ms': latest_metrics.response_time_ms,
                    'uptime_percentage': latest_metrics.uptime_percentage,
                    'error_rate': latest_metrics.error_rate
                },
                'resource_utilization': resource_summary,
                'federation_performance': federation_summary,
                'trends': trends.get('trends', {}),
                'optimization_recommendations': trends.get('recommendations', [])
            }
            
        except Exception as e:
            print(f"❌ Failed to get performance summary: {e}")
            return {'error': str(e)}
    
    async def get_enterprise_performance_metrics(self) -> Dict[str, Any]:
        """Get enterprise-wide performance metrics (async)"""
        try:
            # Get enterprise metrics summary
            enterprise_summary = await self.metrics_repo.get_enterprise_metrics_summary()
            
            # Get performance trends across all federations
            all_registries = await self.registry_repo.get_all(limit=1000)
            
            total_federations = len(all_registries)
            active_federations = len([r for r in all_registries if r.lifecycle_status == 'active'])
            
            # Calculate enterprise performance score
            enterprise_scores = []
            for registry in all_registries:
                metrics = await self.metrics_repo.get_latest_by_registry_id(registry.registry_id)
                if metrics:
                    score = await metrics.calculate_overall_performance_score()
                    enterprise_scores.append(score)
            
            avg_enterprise_score = sum(enterprise_scores) / len(enterprise_scores) if enterprise_scores else 0.0
            
            return {
                'enterprise_overview': {
                    'total_federations': total_federations,
                    'active_federations': active_federations,
                    'inactive_federations': total_federations - active_federations
                },
                'performance_metrics': {
                    'avg_enterprise_score': round(avg_enterprise_score, 2),
                    'avg_health_score': enterprise_summary.get('avg_health_score', 0.0),
                    'avg_response_time': enterprise_summary.get('avg_response_time', 0.0),
                    'avg_uptime': enterprise_summary.get('avg_uptime', 0.0)
                },
                'efficiency_metrics': {
                    'avg_federation_efficiency': enterprise_summary.get('avg_federation_efficiency', 0.0),
                    'avg_privacy_preservation': enterprise_summary.get('avg_privacy_preservation', 0.0),
                    'avg_model_quality': enterprise_summary.get('avg_model_quality', 0.0)
                },
                'summary_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to get enterprise performance metrics: {e}")
            return {'error': str(e)}
    
    async def generate_performance_report(
        self,
        registry_id: str,
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate detailed performance report (async)"""
        try:
            if report_type == "comprehensive":
                # Get comprehensive analysis
                trends = await self.analyze_performance_trends(registry_id, days=30)
                summary = await self.get_performance_summary(registry_id)
                
                report = {
                    'report_type': 'comprehensive',
                    'registry_id': registry_id,
                    'generated_date': datetime.now().isoformat(),
                    'analysis_period_days': 30,
                    'executive_summary': {
                        'overall_performance': summary.get('overall_performance_score', 0.0),
                        'trend_direction': trends.get('trends', {}).get('health_score', {}).get('trend', 'unknown'),
                        'key_insights': self._extract_key_insights(trends, summary)
                    },
                    'detailed_analysis': trends,
                    'performance_summary': summary,
                    'recommendations': trends.get('recommendations', [])
                }
                
            elif report_type == "executive":
                # Get executive summary
                summary = await self.get_performance_summary(registry_id)
                trends = await self.analyze_performance_trends(registry_id, days=7)
                
                report = {
                    'report_type': 'executive',
                    'registry_id': registry_id,
                    'generated_date': datetime.now().isoformat(),
                    'analysis_period_days': 7,
                    'key_metrics': {
                        'performance_score': summary.get('overall_performance_score', 0.0),
                        'health_score': summary.get('current_metrics', {}).get('health_score', 0.0),
                        'uptime': summary.get('current_metrics', {}).get('uptime_percentage', 0.0)
                    },
                    'trends': trends.get('trends', {}),
                    'top_recommendations': trends.get('recommendations', [])[:5]
                }
            
            else:
                return {'error': f'Unknown report type: {report_type}'}
            
            return report
            
        except Exception as e:
            print(f"❌ Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    def _extract_key_insights(
        self,
        trends: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> List[str]:
        """Extract key insights from analysis data"""
        insights = []
        
        # Performance insights
        if summary.get('overall_performance_score', 0) > 80.0:
            insights.append("Excellent overall performance maintained")
        elif summary.get('overall_performance_score', 0) < 60.0:
            insights.append("Performance improvement needed")
        
        # Trend insights
        health_trend = trends.get('trends', {}).get('health_score', {}).get('trend')
        if health_trend == 'improving':
            insights.append("Health score showing positive trend")
        elif health_trend == 'declining':
            insights.append("Health score declining - attention required")
        
        # Resource insights
        resource_summary = summary.get('resource_utilization', {})
        if resource_summary.get('cpu', {}).get('status') == 'high':
            insights.append("High CPU usage detected")
        if resource_summary.get('memory', {}).get('status') == 'high':
            insights.append("High memory usage detected")
        
        return insights
