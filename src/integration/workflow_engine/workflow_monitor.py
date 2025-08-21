"""
Workflow Monitor Service

This module provides real-time monitoring, alerting, and performance analytics
for the cross-module workflow engine.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable
from uuid import UUID

from .models import (
    WorkflowInstance,
    WorkflowTask,
    WorkflowStatus,
    TaskStatus,
    WorkflowMetrics
)


logger = logging.getLogger(__name__)


class WorkflowMonitor:
    """
    Monitors workflow execution, performance, and health.
    
    The workflow monitor provides:
    - Real-time workflow monitoring
    - Performance analytics and metrics
    - Alerting and notifications
    - Health checks and diagnostics
    - Performance optimization recommendations
    """
    
    def __init__(self):
        """Initialize the workflow monitor."""
        self.monitored_workflows: Dict[UUID, WorkflowInstance] = {}
        self.workflow_metrics: Dict[UUID, WorkflowMetrics] = {}
        self.performance_thresholds: Dict[str, Dict[str, float]] = {
            "execution_time": {
                "warning": 300.0,  # 5 minutes
                "critical": 1800.0  # 30 minutes
            },
            "success_rate": {
                "warning": 0.95,  # 95%
                "critical": 0.80   # 80%
            },
            "resource_utilization": {
                "warning": 0.80,  # 80%
                "critical": 0.95   # 95%
            }
        }
        
        # Alert handlers
        self.alert_handlers: Dict[str, Callable] = {}
        
        # Performance tracking
        self.performance_history: Dict[UUID, List[Dict[str, Any]]] = {}
        self.global_metrics = {
            "total_workflows_monitored": 0,
            "active_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "average_execution_time": 0.0,
            "overall_success_rate": 0.0
        }
        
        # Background monitoring
        self.is_running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._metrics_collection_task: Optional[asyncio.Task] = None
        self._alert_check_task: Optional[asyncio.Task] = None
        
        logger.info("Workflow monitor initialized")
    
    async def start_monitoring(self) -> None:
        """Start the workflow monitoring service."""
        if self.is_running:
            logger.warning("Workflow monitor is already running")
            return
        
        self.is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._metrics_collection_task = asyncio.create_task(self._metrics_collection_loop())
        self._alert_check_task = asyncio.create_task(self._alert_check_loop())
        logger.info("Workflow monitor started")
    
    async def stop_monitoring(self) -> None:
        """Stop the workflow monitoring service."""
        if not self.is_running:
            logger.warning("Workflow monitor is not running")
            return
        
        self.is_running = False
        
        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._metrics_collection_task:
            self._metrics_collection_task.cancel()
            try:
                await self._metrics_collection_task
            except asyncio.CancelledError:
                pass
        
        if self._alert_check_task:
            self._alert_check_task.cancel()
            try:
                await self._alert_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Workflow monitor stopped")
    
    def register_workflow_for_monitoring(self, workflow_instance: WorkflowInstance) -> None:
        """Register a workflow instance for monitoring."""
        self.monitored_workflows[workflow_instance.instance_id] = workflow_instance
        
        # Initialize metrics
        self.workflow_metrics[workflow_instance.instance_id] = WorkflowMetrics(
            workflow_id=workflow_instance.workflow_id,
            instance_id=workflow_instance.instance_id
        )
        
        # Initialize performance history
        self.performance_history[workflow_instance.instance_id] = []
        
        self.global_metrics["total_workflows_monitored"] += 1
        self.global_metrics["active_workflows"] += 1
        
        logger.info(f"Registered workflow for monitoring: {workflow_instance.instance_id}")
    
    def unregister_workflow_from_monitoring(self, workflow_id: UUID) -> None:
        """Unregister a workflow instance from monitoring."""
        if workflow_id in self.monitored_workflows:
            del self.monitored_workflows[workflow_id]
            
            if workflow_id in self.workflow_metrics:
                del self.workflow_metrics[workflow_id]
            
            if workflow_id in self.performance_history:
                del self.performance_history[workflow_id]
            
            self.global_metrics["active_workflows"] -= 1
            logger.info(f"Unregistered workflow from monitoring: {workflow_id}")
    
    def update_workflow_status(self, workflow_id: UUID, status: WorkflowStatus) -> None:
        """Update the status of a monitored workflow."""
        if workflow_id in self.monitored_workflows:
            instance = self.monitored_workflows[workflow_id]
            instance.status = status
            
            # Update metrics
            if workflow_id in self.workflow_metrics:
                metrics = self.workflow_metrics[workflow_id]
                if status == WorkflowStatus.COMPLETED:
                    metrics.successful_executions += 1
                    metrics.last_success = datetime.utcnow()
                    self.global_metrics["completed_workflows"] += 1
                    self.global_metrics["active_workflows"] -= 1
                elif status == WorkflowStatus.FAILED:
                    metrics.failed_executions += 1
                    metrics.last_failure = datetime.utcnow()
                    self.global_metrics["failed_workflows"] += 1
                    self.global_metrics["active_workflows"] -= 1
                
                metrics.total_executions += 1
                metrics.last_execution = datetime.utcnow()
            
            logger.debug(f"Updated workflow status: {workflow_id} -> {status}")
    
    def update_task_status(self, workflow_id: UUID, task_id: UUID, status: TaskStatus) -> None:
        """Update the status of a task within a monitored workflow."""
        if workflow_id in self.monitored_workflows:
            instance = self.monitored_workflows[workflow_id]
            for task in instance.tasks:
                if task.task_id == task_id:
                    task.status = status
                    break
            
            logger.debug(f"Updated task status: {workflow_id}:{task_id} -> {status}")
    
    def set_performance_thresholds(self, metric: str, thresholds: Dict[str, float]) -> None:
        """Set performance thresholds for a specific metric."""
        self.performance_thresholds[metric] = thresholds
        logger.info(f"Updated performance thresholds for {metric}: {thresholds}")
    
    def register_alert_handler(self, alert_type: str, handler: Callable) -> None:
        """Register an alert handler for a specific alert type."""
        self.alert_handlers[alert_type] = handler
        logger.info(f"Registered alert handler for type: {alert_type}")
    
    def get_workflow_metrics(self, workflow_id: UUID) -> Optional[WorkflowMetrics]:
        """Get metrics for a specific workflow."""
        return self.workflow_metrics.get(workflow_id)
    
    def get_workflow_performance_history(self, workflow_id: UUID, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance history for a specific workflow."""
        if workflow_id not in self.performance_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        history = self.performance_history[workflow_id]
        
        return [
            entry for entry in history 
            if entry.get("timestamp", datetime.min) > cutoff_time
        ]
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global performance metrics."""
        # Calculate overall success rate
        total = self.global_metrics["completed_workflows"] + self.global_metrics["failed_workflows"]
        if total > 0:
            self.global_metrics["overall_success_rate"] = (
                self.global_metrics["completed_workflows"] / total
            )
        
        return self.global_metrics.copy()
    
    def get_performance_alerts(self, severity: str = "all") -> List[Dict[str, Any]]:
        """Get current performance alerts."""
        alerts = []
        
        for workflow_id, metrics in self.workflow_metrics.items():
            workflow_alerts = self._check_workflow_alerts(workflow_id, metrics)
            if severity == "all" or any(alert["severity"] == severity for alert in workflow_alerts):
                alerts.extend(workflow_alerts)
        
        return alerts
    
    def get_workflow_health_summary(self) -> Dict[str, Any]:
        """Get a summary of workflow health across all monitored workflows."""
        total_workflows = len(self.monitored_workflows)
        if total_workflows == 0:
            return {"status": "no_workflows", "message": "No workflows are currently monitored"}
        
        # Calculate health metrics
        healthy_workflows = 0
        warning_workflows = 0
        critical_workflows = 0
        
        for workflow_id, metrics in self.workflow_metrics.items():
            health_status = self._assess_workflow_health(workflow_id, metrics)
            if health_status == "healthy":
                healthy_workflows += 1
            elif health_status == "warning":
                warning_workflows += 1
            elif health_status == "critical":
                critical_workflows += 1
        
        # Determine overall health
        if critical_workflows > 0:
            overall_status = "critical"
        elif warning_workflows > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "total_workflows": total_workflows,
            "healthy_workflows": healthy_workflows,
            "warning_workflows": warning_workflows,
            "critical_workflows": critical_workflows,
            "health_percentage": (healthy_workflows / total_workflows) * 100
        }
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for tracking workflow status."""
        logger.info("Starting workflow monitoring loop")
        
        while self.is_running:
            try:
                # Update workflow progress
                await self._update_workflow_progress()
                
                # Check for completed workflows
                await self._check_completed_workflows()
                
                # Wait before next iteration
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                logger.info("Workflow monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in workflow monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
        
        logger.info("Workflow monitoring loop stopped")
    
    async def _metrics_collection_loop(self) -> None:
        """Background loop for collecting performance metrics."""
        logger.info("Starting metrics collection loop")
        
        while self.is_running:
            try:
                # Collect performance metrics
                await self._collect_performance_metrics()
                
                # Wait before next collection
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except asyncio.CancelledError:
                logger.info("Metrics collection loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
        
        logger.info("Metrics collection loop stopped")
    
    async def _alert_check_loop(self) -> None:
        """Background loop for checking performance alerts."""
        logger.info("Starting alert check loop")
        
        while self.is_running:
            try:
                # Check for performance alerts
                await self._check_performance_alerts()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                logger.info("Alert check loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
                await asyncio.sleep(120)  # Wait before retrying
        
        logger.info("Alert check loop stopped")
    
    async def _update_workflow_progress(self) -> None:
        """Update progress for running workflows."""
        for workflow_id, instance in self.monitored_workflows.items():
            if instance.status == WorkflowStatus.RUNNING:
                # Calculate progress based on completed tasks
                total_tasks = len(instance.tasks)
                completed_tasks = sum(1 for task in instance.tasks if task.status == TaskStatus.COMPLETED)
                
                if total_tasks > 0:
                    instance.progress = (completed_tasks / total_tasks) * 100
                
                logger.debug(f"Updated workflow progress: {workflow_id} -> {instance.progress:.1f}%")
    
    async def _check_completed_workflows(self) -> None:
        """Check for workflows that have completed."""
        for workflow_id, instance in list(self.monitored_workflows.items()):
            if instance.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                # Calculate execution time
                if instance.started_at and instance.completed_at:
                    execution_time = (instance.completed_at - instance.started_at).total_seconds()
                    
                    # Update metrics
                    if workflow_id in self.workflow_metrics:
                        metrics = self.workflow_metrics[workflow_id]
                        metrics.total_execution_time += execution_time
                        
                        # Update min/max execution times
                        if metrics.min_execution_time == 0 or execution_time < metrics.min_execution_time:
                            metrics.min_execution_time = execution_time
                        if execution_time > metrics.max_execution_time:
                            metrics.max_execution_time = execution_time
                        
                        # Update average execution time
                        if metrics.total_executions > 0:
                            metrics.average_execution_time = metrics.total_execution_time / metrics.total_executions
                
                logger.info(f"Workflow completed: {workflow_id} with status {instance.status}")
    
    async def _collect_performance_metrics(self) -> None:
        """Collect performance metrics for all monitored workflows."""
        for workflow_id, instance in self.monitored_workflows.items():
            if instance.status == WorkflowStatus.RUNNING:
                # Collect current performance snapshot
                snapshot = {
                    "timestamp": datetime.utcnow(),
                    "progress": instance.progress,
                    "running_tasks": sum(1 for task in instance.tasks if task.status == TaskStatus.RUNNING),
                    "completed_tasks": sum(1 for task in instance.tasks if task.status == TaskStatus.COMPLETED),
                    "failed_tasks": sum(1 for task in instance.tasks if task.status == TaskStatus.FAILED)
                }
                
                if workflow_id in self.performance_history:
                    self.performance_history[workflow_id].append(snapshot)
                
                logger.debug(f"Collected performance snapshot for workflow: {workflow_id}")
    
    async def _check_performance_alerts(self) -> None:
        """Check for performance alerts across all monitored workflows."""
        for workflow_id, metrics in self.workflow_metrics.items():
            alerts = self._check_workflow_alerts(workflow_id, metrics)
            
            for alert in alerts:
                await self._trigger_alert(alert)
    
    def _check_workflow_alerts(self, workflow_id: UUID, metrics: WorkflowMetrics) -> List[Dict[str, Any]]:
        """Check for alerts for a specific workflow."""
        alerts = []
        
        # Check execution time
        if metrics.average_execution_time > self.performance_thresholds["execution_time"]["critical"]:
            alerts.append({
                "workflow_id": workflow_id,
                "alert_type": "execution_time",
                "severity": "critical",
                "message": f"Average execution time {metrics.average_execution_time:.1f}s exceeds critical threshold",
                "timestamp": datetime.utcnow()
            })
        elif metrics.average_execution_time > self.performance_thresholds["execution_time"]["warning"]:
            alerts.append({
                "workflow_id": workflow_id,
                "alert_type": "execution_time",
                "severity": "warning",
                "message": f"Average execution time {metrics.average_execution_time:.1f}s exceeds warning threshold",
                "timestamp": datetime.utcnow()
            })
        
        # Check success rate
        if metrics.total_executions > 0:
            success_rate = metrics.successful_executions / metrics.total_executions
            if success_rate < self.performance_thresholds["success_rate"]["critical"]:
                alerts.append({
                    "workflow_id": workflow_id,
                    "alert_type": "success_rate",
                    "severity": "critical",
                    "message": f"Success rate {success_rate:.1%} below critical threshold",
                    "timestamp": datetime.utcnow()
                })
            elif success_rate < self.performance_thresholds["success_rate"]["warning"]:
                alerts.append({
                    "workflow_id": workflow_id,
                    "alert_type": "success_rate",
                    "severity": "warning",
                    "message": f"Success rate {success_rate:.1%} below warning threshold",
                    "timestamp": datetime.utcnow()
                })
        
        return alerts
    
    def _assess_workflow_health(self, workflow_id: UUID, metrics: WorkflowMetrics) -> str:
        """Assess the health of a specific workflow."""
        # Check for critical alerts
        alerts = self._check_workflow_alerts(workflow_id, metrics)
        if any(alert["severity"] == "critical" for alert in alerts):
            return "critical"
        
        # Check for warning alerts
        if any(alert["severity"] == "warning" for alert in alerts):
            return "warning"
        
        return "healthy"
    
    async def _trigger_alert(self, alert: Dict[str, Any]) -> None:
        """Trigger an alert using registered handlers."""
        alert_type = alert["alert_type"]
        
        if alert_type in self.alert_handlers:
            try:
                handler = self.alert_handlers[alert_type]
                await handler(alert)
                logger.info(f"Alert triggered via handler: {alert_type} - {alert['message']}")
            except Exception as e:
                logger.error(f"Error in alert handler {alert_type}: {e}")
        else:
            # Default alert handling
            logger.warning(f"Alert: {alert['severity'].upper()} - {alert['message']}")
    
    def get_performance_recommendations(self, workflow_id: UUID) -> List[str]:
        """Get performance optimization recommendations for a workflow."""
        recommendations = []
        
        if workflow_id not in self.workflow_metrics:
            return recommendations
        
        metrics = self.workflow_metrics[workflow_id]
        
        # Check execution time
        if metrics.average_execution_time > self.performance_thresholds["execution_time"]["warning"]:
            recommendations.append("Consider optimizing task execution or reducing workflow complexity")
        
        # Check success rate
        if metrics.total_executions > 0:
            success_rate = metrics.successful_executions / metrics.total_executions
            if success_rate < self.performance_thresholds["success_rate"]["warning"]:
                recommendations.append("Investigate task failures and improve error handling")
        
        # Check resource utilization
        if metrics.total_executions > 0:
            avg_time = metrics.average_execution_time
            if avg_time > 0:
                throughput = 1.0 / avg_time
                if throughput < 0.1:  # Less than 0.1 workflows per second
                    recommendations.append("Consider parallelizing tasks or optimizing resource allocation")
        
        return recommendations
