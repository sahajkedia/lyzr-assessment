"""
Real Calendly API Client.
Handles authentication and API calls to Calendly's servers.
"""
import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CalendlyConfig:
    """Configuration for Calendly API."""
    api_key: str
    api_base_url: str = "https://api.calendly.com"
    organization_uri: Optional[str] = None
    user_uri: Optional[str] = None
    default_event_type_uri: Optional[str] = None
    timeout: float = 30.0


class CalendlyAPIError(Exception):
    """Exception raised for Calendly API errors."""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class CalendlyClient:
    """
    Real Calendly API Client.
    
    Handles:
    - Authentication via Personal Access Token (PAT)
    - Get current user info
    - List event types
    - Get availability
    - Create scheduled events (via Scheduling API)
    - Get scheduled events
    - Cancel events
    """
    
    def __init__(self, config: CalendlyConfig = None):
        """Initialize the Calendly client."""
        if config is None:
            api_key = os.getenv("CALENDLY_API_KEY", "")
            config = CalendlyConfig(
                api_key=api_key,
                organization_uri=os.getenv("CALENDLY_ORGANIZATION_URI"),
                user_uri=os.getenv("CALENDLY_USER_URI"),
                default_event_type_uri=os.getenv("CALENDLY_EVENT_TYPE_URI"),
            )
        
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._user_info: Optional[Dict[str, Any]] = None
        self._event_types: Optional[List[Dict[str, Any]]] = None
        
    @property
    def is_configured(self) -> bool:
        """Check if Calendly is properly configured."""
        return bool(self.config.api_key and len(self.config.api_key) > 10)
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.api_base_url,
                headers=self.headers,
                timeout=self.config.timeout,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None,
    ) -> Dict[str, Any]:
        """Make an API request to Calendly."""
        client = await self._get_client()
        
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            
            if response.status_code == 401:
                raise CalendlyAPIError(
                    "Invalid or expired API key",
                    status_code=401,
                )
            
            if response.status_code == 403:
                raise CalendlyAPIError(
                    "Access forbidden - check API permissions",
                    status_code=403,
                )
            
            if response.status_code == 404:
                raise CalendlyAPIError(
                    "Resource not found",
                    status_code=404,
                )
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise CalendlyAPIError(
                    f"API error: {error_data.get('message', 'Unknown error')}",
                    status_code=response.status_code,
                    response_data=error_data,
                )
            
            return response.json() if response.content else {}
            
        except httpx.TimeoutException:
            raise CalendlyAPIError("Request timed out")
        except httpx.RequestError as e:
            raise CalendlyAPIError(f"Request failed: {str(e)}")
    
    # ==================== User & Organization ====================
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user info."""
        if self._user_info:
            return self._user_info
        
        response = await self._request("GET", "/users/me")
        self._user_info = response.get("resource", {})
        
        # Cache organization and user URIs
        if not self.config.organization_uri:
            self.config.organization_uri = self._user_info.get("current_organization")
        if not self.config.user_uri:
            self.config.user_uri = self._user_info.get("uri")
        
        logger.info(f"Calendly connected as: {self._user_info.get('name')}")
        return self._user_info
    
    async def verify_connection(self) -> bool:
        """Verify the API connection is working."""
        try:
            await self.get_current_user()
            return True
        except CalendlyAPIError as e:
            logger.error(f"Calendly connection failed: {e.message}")
            return False
    
    # ==================== Event Types ====================
    
    async def get_event_types(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all event types for the organization."""
        if self._event_types:
            return self._event_types
        
        # Ensure we have organization URI
        if not self.config.organization_uri:
            await self.get_current_user()
        
        params = {
            "organization": self.config.organization_uri,
        }
        
        if active_only:
            params["active"] = "true"
        
        response = await self._request("GET", "/event_types", params=params)
        self._event_types = response.get("collection", [])
        
        logger.info(f"Found {len(self._event_types)} event types")
        return self._event_types
    
    async def get_event_type_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get event type by slug/name."""
        event_types = await self.get_event_types()
        
        # Try exact match first
        for et in event_types:
            if et.get("slug") == slug or et.get("name", "").lower() == slug.lower():
                return et
        
        # Try partial match
        for et in event_types:
            if slug.lower() in et.get("name", "").lower():
                return et
        
        return None
    
    # ==================== Availability ====================
    
    async def get_user_availability(
        self,
        start_time: str,
        end_time: str,
        event_type_uri: str = None,
    ) -> Dict[str, Any]:
        """
        Get user availability for a date range.
        
        Args:
            start_time: ISO 8601 datetime (e.g., "2025-11-26T00:00:00Z")
            end_time: ISO 8601 datetime (e.g., "2025-11-26T23:59:59Z")
            event_type_uri: Optional specific event type URI
        """
        if not self.config.user_uri:
            await self.get_current_user()
        
        params = {
            "user": self.config.user_uri,
            "start_time": start_time,
            "end_time": end_time,
        }
        
        if event_type_uri:
            params["event_type"] = event_type_uri
        
        response = await self._request("GET", "/user_availability_schedules", params=params)
        return response
    
    async def get_available_times(
        self,
        event_type_uri: str,
        start_time: str,
        end_time: str,
    ) -> List[Dict[str, Any]]:
        """
        Get available booking times for an event type.
        Uses the Scheduling API availability endpoint.
        
        Args:
            event_type_uri: Event type URI
            start_time: ISO 8601 start datetime
            end_time: ISO 8601 end datetime
            
        Returns:
            List of available time slots
        """
        params = {
            "event_type": event_type_uri,
            "start_time": start_time,
            "end_time": end_time,
        }
        
        response = await self._request("GET", "/event_type_available_times", params=params)
        return response.get("collection", [])
    
    # ==================== Scheduled Events ====================
    
    async def list_scheduled_events(
        self,
        min_start_time: str = None,
        max_start_time: str = None,
        status: str = "active",
        count: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List scheduled events.
        
        Args:
            min_start_time: Filter by minimum start time (ISO 8601)
            max_start_time: Filter by maximum start time (ISO 8601)
            status: Event status: "active", "canceled"
            count: Max number of events to return
        """
        if not self.config.user_uri:
            await self.get_current_user()
        
        params = {
            "user": self.config.user_uri,
            "status": status,
            "count": min(count, 100),
        }
        
        if min_start_time:
            params["min_start_time"] = min_start_time
        if max_start_time:
            params["max_start_time"] = max_start_time
        
        response = await self._request("GET", "/scheduled_events", params=params)
        return response.get("collection", [])
    
    async def get_scheduled_event(self, event_uuid: str) -> Dict[str, Any]:
        """Get a specific scheduled event by UUID."""
        response = await self._request("GET", f"/scheduled_events/{event_uuid}")
        return response.get("resource", {})
    
    async def get_event_invitees(self, event_uuid: str) -> List[Dict[str, Any]]:
        """Get invitees for a scheduled event."""
        response = await self._request("GET", f"/scheduled_events/{event_uuid}/invitees")
        return response.get("collection", [])
    
    # ==================== Scheduling API (Create Events) ====================
    
    async def create_scheduled_event(
        self,
        event_type_uri: str,
        start_time: str,
        invitee_email: str,
        invitee_name: str,
        invitee_phone: str = None,
        custom_answers: List[Dict] = None,
        timezone: str = "UTC",
    ) -> Dict[str, Any]:
        """
        Create a scheduled event using the Scheduling API.
        
        Args:
            event_type_uri: Event type URI
            start_time: Start time in ISO 8601 format
            invitee_email: Invitee's email
            invitee_name: Invitee's name
            invitee_phone: Optional phone number
            custom_answers: Optional custom question answers
            timezone: Timezone for the booking
            
        Returns:
            Created event details
        """
        payload = {
            "event_type_uuid": self._extract_uuid(event_type_uri),
            "start_time": start_time,
            "invitee": {
                "email": invitee_email,
                "name": invitee_name,
                "timezone": timezone,
            }
        }
        
        if invitee_phone:
            payload["invitee"]["phone_number"] = invitee_phone
        
        if custom_answers:
            payload["invitee"]["questions_and_answers"] = custom_answers
        
        # The Scheduling API endpoint
        response = await self._request("POST", "/scheduled_events", json_data=payload)
        return response.get("resource", response)
    
    async def cancel_scheduled_event(
        self,
        event_uuid: str,
        reason: str = None,
    ) -> Dict[str, Any]:
        """
        Cancel a scheduled event.
        
        Args:
            event_uuid: Event UUID
            reason: Optional cancellation reason
        """
        payload = {}
        if reason:
            payload["reason"] = reason
        
        response = await self._request(
            "POST",
            f"/scheduled_events/{event_uuid}/cancellation",
            json_data=payload,
        )
        return response.get("resource", response)
    
    # ==================== Webhooks ====================
    
    async def create_webhook_subscription(
        self,
        url: str,
        events: List[str],
        scope: str = "user",
    ) -> Dict[str, Any]:
        """
        Create a webhook subscription.
        
        Args:
            url: Webhook callback URL
            events: List of events to subscribe to
                   (e.g., ["invitee.created", "invitee.canceled"])
            scope: "user" or "organization"
        """
        if not self.config.organization_uri:
            await self.get_current_user()
        
        payload = {
            "url": url,
            "events": events,
            "scope": scope,
        }
        
        if scope == "organization":
            payload["organization"] = self.config.organization_uri
        else:
            payload["user"] = self.config.user_uri
        
        response = await self._request("POST", "/webhook_subscriptions", json_data=payload)
        return response.get("resource", response)
    
    async def list_webhook_subscriptions(self) -> List[Dict[str, Any]]:
        """List all webhook subscriptions."""
        if not self.config.organization_uri:
            await self.get_current_user()
        
        params = {
            "organization": self.config.organization_uri,
            "scope": "organization",
        }
        
        response = await self._request("GET", "/webhook_subscriptions", params=params)
        return response.get("collection", [])
    
    async def delete_webhook_subscription(self, webhook_uuid: str) -> bool:
        """Delete a webhook subscription."""
        await self._request("DELETE", f"/webhook_subscriptions/{webhook_uuid}")
        return True
    
    # ==================== Helpers ====================
    
    def _extract_uuid(self, uri: str) -> str:
        """Extract UUID from Calendly URI."""
        if "/" in uri:
            return uri.split("/")[-1]
        return uri
    
    def format_datetime_for_api(self, date_str: str, time_str: str, timezone: str = "UTC") -> str:
        """
        Format date and time for Calendly API.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            time_str: Time in HH:MM format
            timezone: Timezone (default UTC)
            
        Returns:
            ISO 8601 datetime string
        """
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# Global client instance
calendly_client = CalendlyClient()

