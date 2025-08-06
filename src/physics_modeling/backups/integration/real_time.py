"""
Real-Time Data Connector for Physics Modeling

This module provides real-time data integration capabilities for physics-based modeling,
enabling live sensor data streams, real-time monitoring, and dynamic model updates.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np


class DataStreamType(Enum):
    """Types of real-time data streams"""
    SENSOR_DATA = "sensor_data"
    SIMULATION_RESULTS = "simulation_results"
    CONTROL_SIGNALS = "control_signals"
    ALARM_EVENTS = "alarm_events"
    PERFORMANCE_METRICS = "performance_metrics"


class ConnectionStatus(Enum):
    """Connection status for real-time data streams"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class DataPoint:
    """Represents a single data point from a real-time stream"""
    timestamp: float
    value: float
    unit: str
    sensor_id: str
    location: str
    quality: float = 1.0  # Data quality indicator (0-1)
    metadata: Dict[str, Any] = None


@dataclass
class StreamConfig:
    """Configuration for a real-time data stream"""
    stream_id: str
    stream_type: DataStreamType
    update_frequency: float  # Hz
    buffer_size: int = 1000
    timeout: float = 30.0
    retry_attempts: int = 3
    filters: Dict[str, Any] = None


class RealTimeConnector:
    """
    Real-time data connector for physics modeling
    
    This class provides capabilities for:
    - Connecting to real-time data sources
    - Streaming sensor data for physics models
    - Monitoring system performance
    - Triggering model updates based on live data
    - Handling data quality and validation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the real-time connector
        
        Args:
            config: Configuration dictionary for the connector
        """
        self.config = config or {}
        self.status = ConnectionStatus.DISCONNECTED
        self.active_streams: Dict[str, StreamConfig] = {}
        self.data_buffers: Dict[str, List[DataPoint]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.connection_handlers: Dict[str, Any] = {}
        
        # Performance metrics
        self.metrics = {
            'total_data_points': 0,
            'data_rate': 0.0,  # points per second
            'error_count': 0,
            'last_update': time.time()
        }
    
    async def connect(self, endpoint: str, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to a real-time data endpoint
        
        Args:
            endpoint: Data source endpoint URL
            credentials: Authentication credentials
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.status = ConnectionStatus.CONNECTING
            print(f"🔌 Connecting to real-time data endpoint: {endpoint}")
            
            # Simulate connection process
            await asyncio.sleep(0.1)
            
            # Store connection info
            self.connection_handlers[endpoint] = {
                'endpoint': endpoint,
                'credentials': credentials,
                'connected_at': time.time()
            }
            
            self.status = ConnectionStatus.CONNECTED
            print(f"✅ Connected to real-time data endpoint: {endpoint}")
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            print(f"❌ Failed to connect to {endpoint}: {e}")
            return False
    
    async def disconnect(self, endpoint: str = None) -> bool:
        """
        Disconnect from real-time data endpoint
        
        Args:
            endpoint: Specific endpoint to disconnect from (None for all)
            
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if endpoint:
                if endpoint in self.connection_handlers:
                    del self.connection_handlers[endpoint]
                    print(f"🔌 Disconnected from: {endpoint}")
            else:
                self.connection_handlers.clear()
                print("🔌 Disconnected from all endpoints")
            
            self.status = ConnectionStatus.DISCONNECTED
            return True
            
        except Exception as e:
            print(f"❌ Error during disconnection: {e}")
            return False
    
    def subscribe_to_stream(self, stream_config: StreamConfig) -> bool:
        """
        Subscribe to a real-time data stream
        
        Args:
            stream_config: Configuration for the data stream
            
        Returns:
            True if subscription successful, False otherwise
        """
        try:
            stream_id = stream_config.stream_id
            
            # Initialize buffer for this stream
            self.data_buffers[stream_id] = []
            self.active_streams[stream_id] = stream_config
            self.callbacks[stream_id] = []
            
            print(f"📡 Subscribed to stream: {stream_id}")
            print(f"   Type: {stream_config.stream_type.value}")
            print(f"   Frequency: {stream_config.update_frequency} Hz")
            print(f"   Buffer size: {stream_config.buffer_size}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to subscribe to stream: {e}")
            return False
    
    def unsubscribe_from_stream(self, stream_id: str) -> bool:
        """
        Unsubscribe from a real-time data stream
        
        Args:
            stream_id: ID of the stream to unsubscribe from
            
        Returns:
            True if unsubscription successful, False otherwise
        """
        try:
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
                del self.data_buffers[stream_id]
                del self.callbacks[stream_id]
                print(f"📡 Unsubscribed from stream: {stream_id}")
                return True
            else:
                print(f"⚠️ Stream {stream_id} not found")
                return False
                
        except Exception as e:
            print(f"❌ Error unsubscribing from stream: {e}")
            return False
    
    def add_callback(self, stream_id: str, callback: Callable) -> bool:
        """
        Add a callback function for a data stream
        
        Args:
            stream_id: ID of the stream
            callback: Function to call when new data arrives
            
        Returns:
            True if callback added successfully, False otherwise
        """
        try:
            if stream_id in self.callbacks:
                self.callbacks[stream_id].append(callback)
                print(f"📞 Added callback for stream: {stream_id}")
                return True
            else:
                print(f"⚠️ Stream {stream_id} not found")
                return False
                
        except Exception as e:
            print(f"❌ Error adding callback: {e}")
            return False
    
    async def receive_data(self, stream_id: str, data: DataPoint) -> bool:
        """
        Receive and process incoming data point
        
        Args:
            stream_id: ID of the stream
            data: Incoming data point
            
        Returns:
            True if data processed successfully, False otherwise
        """
        try:
            if stream_id not in self.data_buffers:
                print(f"⚠️ Stream {stream_id} not found")
                return False
            
            # Add to buffer
            buffer = self.data_buffers[stream_id]
            buffer.append(data)
            
            # Maintain buffer size
            config = self.active_streams[stream_id]
            if len(buffer) > config.buffer_size:
                buffer.pop(0)
            
            # Update metrics
            self.metrics['total_data_points'] += 1
            self.metrics['last_update'] = time.time()
            
            # Call registered callbacks
            for callback in self.callbacks.get(stream_id, []):
                try:
                    await callback(data)
                except Exception as e:
                    print(f"❌ Callback error: {e}")
                    self.metrics['error_count'] += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing data: {e}")
            self.metrics['error_count'] += 1
            return False
    
    def get_latest_data(self, stream_id: str, count: int = 1) -> List[DataPoint]:
        """
        Get the latest data points from a stream
        
        Args:
            stream_id: ID of the stream
            count: Number of data points to retrieve
            
        Returns:
            List of latest data points
        """
        try:
            if stream_id not in self.data_buffers:
                return []
            
            buffer = self.data_buffers[stream_id]
            return buffer[-count:] if buffer else []
            
        except Exception as e:
            print(f"❌ Error retrieving data: {e}")
            return []
    
    def get_stream_statistics(self, stream_id: str) -> Dict[str, Any]:
        """
        Get statistics for a data stream
        
        Args:
            stream_id: ID of the stream
            
        Returns:
            Dictionary containing stream statistics
        """
        try:
            if stream_id not in self.data_buffers:
                return {}
            
            buffer = self.data_buffers[stream_id]
            if not buffer:
                return {'data_points': 0}
            
            values = [point.value for point in buffer]
            
            stats = {
                'data_points': len(buffer),
                'min_value': min(values),
                'max_value': max(values),
                'mean_value': np.mean(values),
                'std_value': np.std(values),
                'latest_timestamp': buffer[-1].timestamp,
                'data_rate': len(buffer) / (time.time() - buffer[0].timestamp) if len(buffer) > 1 else 0
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error calculating statistics: {e}")
            return {}
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status and metrics
        
        Returns:
            Dictionary containing status information
        """
        return {
            'status': self.status.value,
            'active_streams': len(self.active_streams),
            'total_connections': len(self.connection_handlers),
            'metrics': self.metrics.copy(),
            'streams': list(self.active_streams.keys())
        }
    
    async def simulate_sensor_data(self, stream_id: str, duration: float = 60.0) -> None:
        """
        Simulate sensor data for testing purposes
        
        Args:
            stream_id: ID of the stream to simulate
            duration: Duration of simulation in seconds
        """
        if stream_id not in self.active_streams:
            print(f"⚠️ Stream {stream_id} not found")
            return
        
        config = self.active_streams[stream_id]
        interval = 1.0 / config.update_frequency
        start_time = time.time()
        
        print(f"🎯 Simulating sensor data for stream: {stream_id}")
        print(f"   Duration: {duration} seconds")
        print(f"   Frequency: {config.update_frequency} Hz")
        
        while time.time() - start_time < duration:
            # Generate simulated data point
            timestamp = time.time()
            value = np.random.normal(100, 10)  # Simulated sensor reading
            data_point = DataPoint(
                timestamp=timestamp,
                value=value,
                unit="°C",
                sensor_id=f"sensor_{stream_id}",
                location="simulation",
                quality=0.95
            )
            
            # Process the data
            await self.receive_data(stream_id, data_point)
            
            # Wait for next update
            await asyncio.sleep(interval)
        
        print(f"✅ Simulation completed for stream: {stream_id}")


# Example usage and templates
class RealTimeTemplates:
    """Templates for common real-time data scenarios"""
    
    @staticmethod
    def temperature_monitoring() -> StreamConfig:
        """Template for temperature monitoring stream"""
        return StreamConfig(
            stream_id="temperature_sensors",
            stream_type=DataStreamType.SENSOR_DATA,
            update_frequency=1.0,  # 1 Hz
            buffer_size=3600,  # 1 hour of data
            filters={'min_quality': 0.8}
        )
    
    @staticmethod
    def pressure_monitoring() -> StreamConfig:
        """Template for pressure monitoring stream"""
        return StreamConfig(
            stream_id="pressure_sensors",
            stream_type=DataStreamType.SENSOR_DATA,
            update_frequency=5.0,  # 5 Hz
            buffer_size=7200,  # 2 hours of data
            filters={'min_quality': 0.9}
        )
    
    @staticmethod
    def simulation_results() -> StreamConfig:
        """Template for simulation results stream"""
        return StreamConfig(
            stream_id="simulation_output",
            stream_type=DataStreamType.SIMULATION_RESULTS,
            update_frequency=0.1,  # 0.1 Hz (every 10 seconds)
            buffer_size=100,
            filters={'convergence_threshold': 1e-6}
        )