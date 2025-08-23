"""
API Client Integration

Integration with external APIs for AASX processing operations.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import time

from ..config.settings import IntegrationConfig

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Exception raised during API operations."""
    pass


class APIClient:
    """Client for external API integration."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize API client.
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self.enabled = config.enable_api_integration
        self.timeout = config.api_timeout_seconds
        self.retry_attempts = config.api_retry_attempts
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0
        self._request_count = 0
        
        # Rate limiting
        self._rate_limit_remaining = 1000
        self._rate_limit_reset = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def _make_request(self, method: str, url: str, 
                           data: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None,
                           retry_count: int = 0) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            url: Request URL
            data: Request data
            headers: Request headers
            retry_count: Current retry attempt
            
        Returns:
            Dict[str, Any]: Response data
        """
        if not self.enabled:
            raise APIError("API integration is disabled")
        
        await self._ensure_session()
        
        # Rate limiting check
        await self._check_rate_limit()
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AASX-Processor/2.0.0'
        }
        if headers:
            request_headers.update(headers)
        
        # Prepare request data
        request_data = None
        if data:
            request_data = json.dumps(data)
        
        start_time = time.time()
        
        try:
            async with self._session.request(
                method, url, data=request_data, headers=request_headers
            ) as response:
                
                # Update rate limiting info
                self._update_rate_limit_info(response)
                
                # Check response status
                if response.status >= 400:
                    error_text = await response.text()
                    raise APIError(f"API request failed: {response.status} - {error_text}")
                
                # Parse response
                try:
                    result = await response.json()
                except Exception:
                    result = {'text': await response.text()}
                
                # Update request tracking
                self._last_request_time = time.time()
                self._request_count += 1
                
                logger.debug(f"API request completed: {method} {url} - {response.status}")
                return result
                
        except asyncio.TimeoutError:
            if retry_count < self.retry_attempts:
                logger.warning(f"API request timed out, retrying ({retry_count + 1}/{self.retry_attempts})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(method, url, data, headers, retry_count + 1)
            else:
                raise APIError(f"API request timed out after {self.retry_attempts} retries")
        
        except Exception as e:
            if retry_count < self.retry_attempts and self._is_retryable_error(e):
                logger.warning(f"API request failed, retrying ({retry_count + 1}/{self.retry_attempts}): {str(e)}")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(method, url, data, headers, retry_count + 1)
            else:
                raise APIError(f"API request failed: {str(e)}")
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if error is retryable."""
        retryable_errors = (
            aiohttp.ClientError,
            aiohttp.ServerDisconnectedError,
            aiohttp.ServerTimeoutError,
            ConnectionError,
            OSError
        )
        return isinstance(error, retryable_errors)
    
    async def _check_rate_limit(self):
        """Check and respect rate limiting."""
        if self._rate_limit_reset and datetime.now() > self._rate_limit_reset:
            self._rate_limit_remaining = 1000
            self._rate_limit_reset = None
        
        if self._rate_limit_remaining <= 0:
            if self._rate_limit_reset:
                wait_time = (self._rate_limit_reset - datetime.now()).total_seconds()
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)
                    self._rate_limit_remaining = 1000
                    self._rate_limit_reset = None
            else:
                # Default rate limiting
                time_since_last = time.time() - self._last_request_time
                if time_since_last < 1.0:  # Max 1 request per second
                    await asyncio.sleep(1.0 - time_since_last)
    
    def _update_rate_limit_info(self, response: aiohttp.ClientResponse):
        """Update rate limiting information from response headers."""
        # Common rate limiting headers
        remaining = response.headers.get('X-RateLimit-Remaining')
        reset_time = response.headers.get('X-RateLimit-Reset')
        
        if remaining:
            try:
                self._rate_limit_remaining = int(remaining)
            except ValueError:
                pass
        
        if reset_time:
            try:
                # Unix timestamp
                reset_timestamp = int(reset_time)
                self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            except ValueError:
                pass
    
    async def get_aasx_info(self, aasx_url: str) -> Dict[str, Any]:
        """
        Get information about AASX file from external API.
        
        Args:
            aasx_url: URL to AASX file
            
        Returns:
            Dict[str, Any]: AASX file information
        """
        url = f"{aasx_url}/info"
        return await self._make_request('GET', url)
    
    async def validate_aasx_remote(self, aasx_url: str, 
                                  validation_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate AASX file using remote API.
        
        Args:
            aasx_url: URL to AASX file
            validation_options: Validation options
            
        Returns:
            Dict[str, Any]: Validation results
        """
        url = f"{aasx_url}/validate"
        data = validation_options or {}
        return await self._make_request('POST', url, data=data)
    
    async def convert_aasx_remote(self, aasx_url: str, target_format: str,
                                 conversion_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert AASX file using remote API.
        
        Args:
            aasx_url: URL to AASX file
            target_format: Target format (json, xml, yaml)
            conversion_options: Conversion options
            
        Returns:
            Dict[str, Any]: Conversion results
        """
        url = f"{aasx_url}/convert"
        data = {
            'target_format': target_format,
            **(conversion_options or {})
        }
        return await self._make_request('POST', url, data=data)
    
    async def extract_aasx_remote(self, aasx_url: str, 
                                 extraction_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract AASX file using remote API.
        
        Args:
            aasx_url: URL to AASX file
            extraction_options: Extraction options
            
        Returns:
            Dict[str, Any]: Extraction results
        """
        url = f"{aasx_url}/extract"
        data = extraction_options or {}
        return await self._make_request('POST', url, data=data)
    
    async def batch_process_remote(self, aasx_urls: List[str], 
                                  operation: str,
                                  operation_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Batch process multiple AASX files using remote API.
        
        Args:
            aasx_urls: List of AASX file URLs
            operation: Operation to perform (validate, convert, extract)
            operation_options: Operation options
            
        Returns:
            Dict[str, Any]: Batch processing results
        """
        url = f"/batch/{operation}"
        data = {
            'files': aasx_urls,
            **(operation_options or {})
        }
        return await self._make_request('POST', url, data=data)
    
    async def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a processing job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dict[str, Any]: Job status
        """
        url = f"/jobs/{job_id}/status"
        return await self._make_request('GET', url)
    
    async def cancel_processing_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a processing job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dict[str, Any]: Cancellation result
        """
        url = f"/jobs/{job_id}/cancel"
        return await self._make_request('POST', url)
    
    async def get_api_status(self) -> Dict[str, Any]:
        """
        Get API service status.
        
        Returns:
            Dict[str, Any]: API status information
        """
        url = "/status"
        return await self._make_request('GET', url)
    
    async def get_api_health(self) -> Dict[str, Any]:
        """
        Get API health information.
        
        Returns:
            Dict[str, Any]: API health status
        """
        url = "/health"
        return await self._make_request('GET', url)
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information and statistics."""
        return {
            'enabled': self.enabled,
            'timeout': self.timeout,
            'retry_attempts': self.retry_attempts,
            'total_requests': self._request_count,
            'last_request_time': self._last_request_time,
            'rate_limit_remaining': self._rate_limit_remaining,
            'rate_limit_reset': self._rate_limit_reset.isoformat() if self._rate_limit_reset else None
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and functionality."""
        test_result = {
            'connection_successful': False,
            'api_available': False,
            'rate_limiting_working': False,
            'errors': []
        }
        
        try:
            # Test basic connectivity
            status = await self.get_api_status()
            test_result['connection_successful'] = True
            test_result['api_available'] = True
            
            # Test rate limiting
            if self._rate_limit_remaining < 1000:
                test_result['rate_limiting_working'] = True
            
            logger.info("API connection test successful")
            
        except Exception as e:
            test_result['errors'].append(str(e))
            logger.error(f"API connection test failed: {str(e)}")
        
        return test_result


class WebhookClient:
    """Client for webhook notifications."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize webhook client.
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self.enabled = config.enable_webhooks
        self.timeout = config.webhook_timeout_seconds
        
        # Webhook endpoints
        self._webhook_endpoints: List[str] = []
        self._webhook_headers: Dict[str, str] = {}
    
    def add_webhook_endpoint(self, url: str, headers: Optional[Dict[str, str]] = None):
        """Add webhook endpoint."""
        self._webhook_endpoints.append(url)
        if headers:
            self._webhook_headers.update(headers)
    
    def remove_webhook_endpoint(self, url: str):
        """Remove webhook endpoint."""
        if url in self._webhook_endpoints:
            self._webhook_endpoints.remove(url)
    
    async def send_webhook(self, event_type: str, data: Dict[str, Any], 
                          endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Send webhook notification.
        
        Args:
            event_type: Type of event
            data: Event data
            endpoint: Specific endpoint (uses all if None)
            
        Returns:
            Dict[str, Any]: Webhook delivery results
        """
        if not self.enabled:
            return {'status': 'disabled', 'endpoints': []}
        
        webhook_data = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        results = []
        endpoints = [endpoint] if endpoint else self._webhook_endpoints
        
        for webhook_url in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook_url,
                        json=webhook_data,
                        headers=self._webhook_headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        result = {
                            'endpoint': webhook_url,
                            'status': response.status,
                            'success': response.status < 400,
                            'response_time': response.headers.get('X-Response-Time', 'unknown')
                        }
                        
                        if response.status >= 400:
                            result['error'] = await response.text()
                        
                        results.append(result)
                        
            except Exception as e:
                results.append({
                    'endpoint': webhook_url,
                    'status': 'error',
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'status': 'completed',
            'total_endpoints': len(endpoints),
            'successful_deliveries': sum(1 for r in results if r['success']),
            'results': results
        }
    
    async def send_processing_complete_webhook(self, job_id: str, result: Dict[str, Any]):
        """Send processing complete webhook."""
        return await self.send_webhook('processing_complete', {
            'job_id': job_id,
            'result': result
        })
    
    async def send_processing_failed_webhook(self, job_id: str, error: str):
        """Send processing failed webhook."""
        return await self.send_webhook('processing_failed', {
            'job_id': job_id,
            'error': error
        })
    
    async def send_validation_complete_webhook(self, file_id: str, validation_result: Dict[str, Any]):
        """Send validation complete webhook."""
        return await self.send_webhook('validation_complete', {
            'file_id': file_id,
            'validation_result': validation_result
        })


# Factory functions
def create_api_client(config: Optional[IntegrationConfig] = None) -> APIClient:
    """Create API client instance."""
    if config is None:
        from ..config.settings import get_environment_config
        config = get_environment_config().integration
    
    return APIClient(config)


def create_webhook_client(config: Optional[IntegrationConfig] = None) -> WebhookClient:
    """Create webhook client instance."""
    if config is None:
        from ..config.settings import get_environment_config
        config = get_environment_config().integration
    
    return WebhookClient(config)
