"""
Time and Date Utilities

Provides comprehensive time and date utilities for the AAS Data Modeling Engine.
Includes timezone handling, date parsing, formatting, and time calculations.
"""

import time
import datetime
from datetime import datetime, date, timezone, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import pytz
import re

logger = logging.getLogger(__name__)


class TimeFormat(Enum):
    """Supported time formats"""
    ISO = "iso"
    RFC3339 = "rfc3339"
    RFC2822 = "rfc2822"
    TIMESTAMP = "timestamp"
    HUMAN = "human"
    CUSTOM = "custom"


@dataclass
class TimeRange:
    """Time range structure"""
    start: datetime
    end: datetime
    duration: timedelta
    
    def __post_init__(self):
        """Calculate duration if not provided"""
        if not hasattr(self, 'duration') or self.duration is None:
            self.duration = self.end - self.start


class TimeUtils:
    """Collection of time and date utilities"""
    
    @staticmethod
    def now(timezone_name: Optional[str] = None) -> datetime:
        """
        Get current datetime with optional timezone
        
        Args:
            timezone_name: Timezone name (e.g., 'UTC', 'America/New_York')
            
        Returns:
            Current datetime in specified timezone
        """
        if timezone_name:
            tz = pytz.timezone(timezone_name)
            return datetime.now(tz)
        else:
            return datetime.now()
    
    @staticmethod
    def utc_now() -> datetime:
        """
        Get current UTC datetime
        
        Returns:
            Current UTC datetime
        """
        return datetime.now(timezone.utc)
    
    @staticmethod
    def parse_datetime(
        date_string: str,
        format_string: Optional[str] = None,
        timezone_name: Optional[str] = None
    ) -> datetime:
        """
        Parse datetime string
        
        Args:
            date_string: String representation of datetime
            format_string: Custom format string
            timezone_name: Timezone name for naive datetimes
            
        Returns:
            Parsed datetime object
        """
        try:
            if format_string:
                dt = datetime.strptime(date_string, format_string)
            else:
                # Try common formats
                dt = TimeUtils._parse_common_formats(date_string)
            
            # Handle timezone
            if dt.tzinfo is None and timezone_name:
                tz = pytz.timezone(timezone_name)
                dt = tz.localize(dt)
            
            return dt
            
        except Exception as e:
            logger.error(f"Failed to parse datetime: {date_string}, error: {e}")
            raise ValueError(f"Invalid datetime format: {date_string}")
    
    @staticmethod
    def _parse_common_formats(date_string: str) -> datetime:
        """Parse common datetime formats"""
        # ISO format
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # RFC 3339 format
        try:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            pass
        
        # RFC 2822 format
        try:
            return datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            pass
        
        # Common date formats
        common_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d/%m/%Y"
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unsupported datetime format: {date_string}")
    
    @staticmethod
    def format_datetime(
        dt: datetime,
        format_type: TimeFormat = TimeFormat.ISO,
        custom_format: Optional[str] = None
    ) -> str:
        """
        Format datetime to string
        
        Args:
            dt: Datetime object to format
            format_type: Type of format to use
            custom_format: Custom format string (for CUSTOM format type)
            
        Returns:
            Formatted datetime string
        """
        if format_type == TimeFormat.ISO:
            return dt.isoformat()
        elif format_type == TimeFormat.RFC3339:
            return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        elif format_type == TimeFormat.RFC2822:
            return dt.strftime("%a, %d %b %Y %H:%M:%S %z")
        elif format_type == TimeFormat.TIMESTAMP:
            return str(int(dt.timestamp()))
        elif format_type == TimeFormat.HUMAN:
            return TimeUtils._format_human_readable(dt)
        elif format_type == TimeFormat.CUSTOM:
            if not custom_format:
                raise ValueError("Custom format string required for CUSTOM format type")
            return dt.strftime(custom_format)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    @staticmethod
    def _format_human_readable(dt: datetime) -> str:
        """Format datetime in human-readable format"""
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            if diff.days == 1:
                return "yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif diff.days < 365:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = diff.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.seconds > 0:
            if diff.seconds < 60:
                return f"{diff.seconds} second{'s' if diff.seconds > 1 else ''} ago"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            return "just now"
    
    @staticmethod
    def convert_timezone(
        dt: datetime,
        target_timezone: str,
        source_timezone: Optional[str] = None
    ) -> datetime:
        """
        Convert datetime to different timezone
        
        Args:
            dt: Datetime object to convert
            target_timezone: Target timezone name
            source_timezone: Source timezone name (if dt is naive)
            
        Returns:
            Datetime in target timezone
        """
        if dt.tzinfo is None:
            if source_timezone:
                source_tz = pytz.timezone(source_timezone)
                dt = source_tz.localize(dt)
            else:
                raise ValueError("Source timezone required for naive datetime")
        
        target_tz = pytz.timezone(target_timezone)
        return dt.astimezone(target_tz)
    
    @staticmethod
    def get_timezone_offset(timezone_name: str) -> timedelta:
        """
        Get timezone offset from UTC
        
        Args:
            timezone_name: Timezone name
            
        Returns:
            Timezone offset from UTC
        """
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        return now.utcoffset()
    
    @staticmethod
    def is_business_day(dt: datetime) -> bool:
        """
        Check if date is a business day
        
        Args:
            dt: Datetime to check
            
        Returns:
            True if business day, False otherwise
        """
        return dt.weekday() < 5  # Monday = 0, Friday = 4
    
    @staticmethod
    def add_business_days(
        dt: datetime,
        days: int,
        holidays: Optional[List[date]] = None
    ) -> datetime:
        """
        Add business days to datetime
        
        Args:
            dt: Starting datetime
            days: Number of business days to add (can be negative)
            holidays: List of holiday dates
            
        Returns:
            Datetime after adding business days
        """
        if holidays is None:
            holidays = []
        
        current = dt
        remaining_days = abs(days)
        direction = 1 if days >= 0 else -1
        
        while remaining_days > 0:
            current += timedelta(days=direction)
            
            # Check if it's a business day and not a holiday
            if (TimeUtils.is_business_day(current) and 
                current.date() not in holidays):
                remaining_days -= 1
        
        return current
    
    @staticmethod
    def get_time_range(
        start: Union[datetime, str],
        end: Union[datetime, str],
        timezone_name: Optional[str] = None
    ) -> TimeRange:
        """
        Create time range object
        
        Args:
            start: Start datetime or string
            end: End datetime or string
            timezone_name: Timezone for string parsing
            
        Returns:
            TimeRange object
        """
        if isinstance(start, str):
            start = TimeUtils.parse_datetime(start, timezone_name=timezone_name)
        if isinstance(end, str):
            end = TimeUtils.parse_datetime(end, timezone_name=timezone_name)
        
        return TimeRange(start=start, end=end, duration=end - start)
    
    @staticmethod
    def split_time_range(
        time_range: TimeRange,
        interval: timedelta
    ) -> List[TimeRange]:
        """
        Split time range into intervals
        
        Args:
            time_range: TimeRange to split
            interval: Interval size
            
        Returns:
            List of TimeRange objects
        """
        ranges = []
        current = time_range.start
        
        while current < time_range.end:
            next_time = min(current + interval, time_range.end)
            ranges.append(TimeRange(start=current, end=next_time, duration=next_time - current))
            current = next_time
        
        return ranges
    
    @staticmethod
    def get_quarter_dates(year: int, quarter: int) -> Tuple[date, date]:
        """
        Get start and end dates for a quarter
        
        Args:
            year: Year
            quarter: Quarter number (1-4)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        if not 1 <= quarter <= 4:
            raise ValueError("Quarter must be between 1 and 4")
        
        quarter_starts = {
            1: date(year, 1, 1),
            2: date(year, 4, 1),
            3: date(year, 7, 1),
            4: date(year, 10, 1)
        }
        
        start_date = quarter_starts[quarter]
        
        if quarter == 4:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            next_quarter = quarter + 1
            end_date = quarter_starts[next_quarter] - timedelta(days=1)
        
        return start_date, end_date
    
    @staticmethod
    def get_week_dates(
        year: int,
        week: int,
        start_day: int = 0  # 0 = Monday, 6 = Sunday
    ) -> Tuple[date, date]:
        """
        Get start and end dates for a week
        
        Args:
            year: Year
            week: Week number (1-53)
            start_day: Day of week to start (0=Monday, 6=Sunday)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        if not 1 <= week <= 53:
            raise ValueError("Week must be between 1 and 53")
        
        # Get January 1st of the year
        jan1 = date(year, 1, 1)
        
        # Find the first Monday of the year
        first_monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)
        
        # Calculate start of the specified week
        week_start = first_monday + timedelta(weeks=week - 1, days=start_day)
        
        # End of week is 6 days later
        week_end = week_start + timedelta(days=6)
        
        return week_start, week_end
    
    @staticmethod
    def format_duration(
        duration: timedelta,
        include_seconds: bool = True,
        short_format: bool = False
    ) -> str:
        """
        Format timedelta to human-readable string
        
        Args:
            duration: Timedelta to format
            include_seconds: Whether to include seconds
            short_format: Whether to use short format (e.g., "2d 3h" vs "2 days 3 hours")
            
        Returns:
            Formatted duration string
        """
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 0:
            return "negative duration"
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        
        if days > 0:
            if short_format:
                parts.append(f"{days}d")
            else:
                parts.append(f"{days} day{'s' if days > 1 else ''}")
        
        if hours > 0:
            if short_format:
                parts.append(f"{hours}h")
            else:
                parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        
        if minutes > 0:
            if short_format:
                parts.append(f"{minutes}m")
            else:
                parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        
        if include_seconds and seconds > 0:
            if short_format:
                parts.append(f"{seconds}s")
            else:
                parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")
        
        if not parts:
            return "0 seconds" if not short_format else "0s"
        
        return " ".join(parts)
    
    @staticmethod
    def parse_duration(duration_string: str) -> timedelta:
        """
        Parse duration string to timedelta
        
        Args:
            duration_string: Duration string (e.g., "2h 30m", "1.5 days")
            
        Returns:
            Timedelta object
        """
        # Common duration patterns
        patterns = [
            (r'(\d+)\s*days?', lambda m: timedelta(days=int(m.group(1)))),
            (r'(\d+)\s*hours?', lambda m: timedelta(hours=int(m.group(1)))),
            (r'(\d+)\s*minutes?', lambda m: timedelta(minutes=int(m.group(1)))),
            (r'(\d+)\s*seconds?', lambda m: timedelta(seconds=int(m.group(1)))),
            (r'(\d+)\s*weeks?', lambda m: timedelta(weeks=int(m.group(1)))),
            (r'(\d+\.\d+)\s*days?', lambda m: timedelta(days=float(m.group(1)))),
            (r'(\d+\.\d+)\s*hours?', lambda m: timedelta(hours=float(m.group(1)))),
            (r'(\d+\.\d+)\s*minutes?', lambda m: timedelta(minutes=float(m.group(1)))),
        ]
        
        total_duration = timedelta()
        remaining_string = duration_string
        
        for pattern, converter in patterns:
            matches = re.findall(pattern, remaining_string, re.IGNORECASE)
            for match in matches:
                total_duration += converter(re.match(pattern, match, re.IGNORECASE))
                remaining_string = re.sub(pattern, '', remaining_string, flags=re.IGNORECASE)
        
        return total_duration
    
    @staticmethod
    def round_datetime(
        dt: datetime,
        interval: timedelta,
        rounding: str = "nearest"
    ) -> datetime:
        """
        Round datetime to nearest interval
        
        Args:
            dt: Datetime to round
            interval: Interval to round to
            rounding: Rounding method ("nearest", "up", "down")
            
        Returns:
            Rounded datetime
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # Convert to timestamp for easier calculation
        timestamp = dt.timestamp()
        interval_seconds = interval.total_seconds()
        
        if rounding == "nearest":
            rounded_timestamp = round(timestamp / interval_seconds) * interval_seconds
        elif rounding == "up":
            rounded_timestamp = (timestamp // interval_seconds + 1) * interval_seconds
        elif rounding == "down":
            rounded_timestamp = (timestamp // interval_seconds) * interval_seconds
        else:
            raise ValueError("Rounding must be 'nearest', 'up', or 'down'")
        
        return datetime.fromtimestamp(rounded_timestamp, tz=dt.tzinfo)
    
    @staticmethod
    def get_age(birth_date: Union[date, datetime]) -> int:
        """
        Calculate age from birth date
        
        Args:
            birth_date: Birth date or datetime
            
        Returns:
            Age in years
        """
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        
        today = date.today()
        age = today.year - birth_date.year
        
        # Adjust age if birthday hasn't occurred this year
        if today < birth_date.replace(year=today.year):
            age -= 1
        
        return age
    
    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Check if year is a leap year
        
        Args:
            year: Year to check
            
        Returns:
            True if leap year, False otherwise
        """
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


# Convenience functions
def now(timezone_name: Optional[str] = None) -> datetime:
    """Convenience function for getting current datetime"""
    return TimeUtils.now(timezone_name)


def utc_now() -> datetime:
    """Convenience function for getting current UTC datetime"""
    return TimeUtils.utc_now()


def parse_datetime(
    date_string: str,
    format_string: Optional[str] = None,
    timezone_name: Optional[str] = None
) -> datetime:
    """Convenience function for parsing datetime strings"""
    return TimeUtils.parse_datetime(date_string, format_string, timezone_name)


def format_datetime(
    dt: datetime,
    format_type: TimeFormat = TimeFormat.ISO,
    custom_format: Optional[str] = None
) -> str:
    """Convenience function for formatting datetime"""
    return TimeUtils.format_datetime(dt, format_type, custom_format)


def convert_timezone(
    dt: datetime,
    target_timezone: str,
    source_timezone: Optional[str] = None
) -> datetime:
    """Convenience function for timezone conversion"""
    return TimeUtils.convert_timezone(dt, target_timezone, source_timezone)


def is_business_day(dt: datetime) -> bool:
    """Convenience function for checking business days"""
    return TimeUtils.is_business_day(dt)


def add_business_days(
    dt: datetime,
    days: int,
    holidays: Optional[List[date]] = None
) -> datetime:
    """Convenience function for adding business days"""
    return TimeUtils.add_business_days(dt, days, holidays)

