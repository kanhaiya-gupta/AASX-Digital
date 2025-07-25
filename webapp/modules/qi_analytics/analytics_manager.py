import sqlite3
from webapp.modules.twin_registry.twin_manager import twin_manager
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

ANALYTICS_DB_PATH = Path('data/aasx_digital.db')  # Use a separate DB if desired

class AnalyticsManager:
    """
    Centralized analytics manager for digital twin metrics, KPIs, and trends.
    All analytics API endpoints should use this class for querying and aggregation.
    This version is decoupled from the live twin registry and uses a dedicated analytics table.
    """
    def __init__(self, db_path: Path = ANALYTICS_DB_PATH):
        self.db_path = db_path
        self._init_analytics_table()

    def _init_analytics_table(self):
        """Create the twin_metrics table if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twin_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twin_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                UNIQUE(twin_id, metric_type, timestamp)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twin_metrics_twin_id ON twin_metrics(twin_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twin_metrics_metric_type ON twin_metrics(metric_type)')
        conn.commit()
        conn.close()

    def get_all_twins_metrics(self, metric_type: str = 'quality_score', days: int = 30) -> List[Dict[str, Any]]:
        """
        Get metrics for all twins from the analytics table.
        Args:
            metric_type (str): The metric to fetch (e.g., 'quality_score').
            days (int): How many days of history to include (default 30).
        Returns:
            List[Dict[str, Any]]: List of twins with their latest metric value.
        """
        since = (datetime.now() - timedelta(days=days)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT twin_id, MAX(timestamp), metric_value
            FROM twin_metrics
            WHERE metric_type = ? AND timestamp >= ?
            GROUP BY twin_id
        ''', (metric_type, since))
        results = cursor.fetchall()
        conn.close()
        return [
            {'twin_id': row[0], 'timestamp': row[1], metric_type: row[2]}
            for row in results
        ]

    def get_twin_metrics(self, twin_id: str, metric_type: str = 'quality_score', days: int = 30) -> List[Dict[str, Any]]:
        """
        Get time series metrics for a specific twin from the analytics table.
        Args:
            twin_id (str): The unique ID of the twin.
            metric_type (str): The metric to fetch.
            days (int): How many days of history to include.
        Returns:
            List[Dict[str, Any]]: List of metric values with timestamps.
        """
        since = (datetime.now() - timedelta(days=days)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, metric_value
            FROM twin_metrics
            WHERE twin_id = ? AND metric_type = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (twin_id, metric_type, since))
        results = cursor.fetchall()
        conn.close()
        return [
            {'timestamp': row[0], metric_type: row[1]}
            for row in results
        ]

    def aggregate_kpis(self, metric_type: str = 'quality_score', days: int = 30) -> Dict[str, Any]:
        """
        Aggregate KPIs across all twins for a given metric and timeframe.
        Args:
            metric_type (str): The metric to aggregate.
            days (int): How many days of history to include.
        Returns:
            Dict[str, Any]: Aggregated KPIs.
        """
        metrics = self.get_all_twins_metrics(metric_type, days)
        if not metrics:
            return {
                f'avg_{metric_type}': 0.0,
                'total_twins': 0
            }
        avg_metric = sum(m[metric_type] for m in metrics) / len(metrics)
        return {
            f'avg_{metric_type}': round(avg_metric, 2),
            'total_twins': len(metrics)
        }

    def insert_metric(self, twin_id: str, metric_type: str, metric_value: float, timestamp: Optional[str] = None):
        """
        Insert a new metric value for a twin into the analytics table.
        Args:
            twin_id (str): The unique ID of the twin.
            metric_type (str): The metric type.
            metric_value (float): The metric value.
            timestamp (str, optional): Timestamp (ISO format). Defaults to now.
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO twin_metrics (twin_id, metric_type, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (twin_id, metric_type, metric_value, timestamp))
        conn.commit()
        conn.close()

# Global analytics manager instance
analytics_manager = AnalyticsManager() 