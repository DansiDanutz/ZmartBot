"""
Time MCP Adapter for Zmarty Dashboard
Provides time management, scheduling, and temporal operations through MCP
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dateutil import parser as date_parser
import pytz
from dataclasses import dataclass, asdict
import calendar

logger = logging.getLogger(__name__)


@dataclass
class TimeEvent:
    """Time-based event data structure"""
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    timezone: str
    event_type: str  # reminder, meeting, alert, analysis, trading_signal
    priority: int  # 1-5 (5 = highest)
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TimeMCPAdapter:
    """
    MCP-compatible time adapter for scheduling and temporal operations
    Provides time zone handling, scheduling, reminders, and time-based analysis
    """
    
    def __init__(self):
        self.events = {}  # In-memory event storage
        self.timezones = {
            'UTC': 'UTC',
            'EST': 'US/Eastern',
            'PST': 'US/Pacific',
            'CST': 'US/Central',
            'MST': 'US/Mountain',
            'GMT': 'GMT',
            'CET': 'Europe/Berlin',
            'JST': 'Asia/Tokyo',
            'AEST': 'Australia/Sydney',
            'IST': 'Asia/Kolkata'
        }
        
        # Market hours for different exchanges
        self.market_hours = {
            'NYSE': {'open': '09:30', 'close': '16:00', 'timezone': 'US/Eastern'},
            'NASDAQ': {'open': '09:30', 'close': '16:00', 'timezone': 'US/Eastern'},
            'LSE': {'open': '08:00', 'close': '16:30', 'timezone': 'Europe/London'},
            'TSE': {'open': '09:00', 'close': '15:00', 'timezone': 'Asia/Tokyo'},
            'CRYPTO': {'open': '00:00', 'close': '23:59', 'timezone': 'UTC', 'always_open': True}
        }
        
        logger.info("Time MCP adapter initialized")
    
    def get_current_time(self, timezone_str: str = 'UTC') -> Dict[str, Any]:
        """Get current time in specified timezone"""
        try:
            # Handle timezone aliases
            tz_name = self.timezones.get(timezone_str, timezone_str)
            tz = pytz.timezone(tz_name)
            current_time = datetime.now(tz)
            
            return {
                'datetime': current_time.isoformat(),
                'timezone': timezone_str,
                'timezone_name': tz_name,
                'timestamp': current_time.timestamp(),
                'unix_timestamp': int(current_time.timestamp()),
                'formatted': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'iso_format': current_time.isoformat(),
                'utc_datetime': current_time.astimezone(pytz.UTC).isoformat(),
                'weekday': current_time.strftime('%A'),
                'month': current_time.strftime('%B'),
                'year': current_time.year,
                'quarter': (current_time.month - 1) // 3 + 1
            }
        except Exception as e:
            logger.error(f"Failed to get current time for timezone {timezone_str}: {e}")
            return {'error': str(e)}
    
    def convert_timezone(
        self, 
        datetime_str: str, 
        from_timezone: str, 
        to_timezone: str
    ) -> Dict[str, Any]:
        """Convert datetime from one timezone to another"""
        try:
            # Parse the datetime string
            dt = date_parser.parse(datetime_str)
            
            # If no timezone info, assume it's in from_timezone
            if dt.tzinfo is None:
                from_tz = pytz.timezone(self.timezones.get(from_timezone, from_timezone))
                dt = from_tz.localize(dt)
            
            # Convert to target timezone
            to_tz = pytz.timezone(self.timezones.get(to_timezone, to_timezone))
            converted_dt = dt.astimezone(to_tz)
            
            return {
                'original_datetime': datetime_str,
                'from_timezone': from_timezone,
                'to_timezone': to_timezone,
                'converted_datetime': converted_dt.isoformat(),
                'formatted': converted_dt.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'timestamp': converted_dt.timestamp(),
                'time_difference_hours': (converted_dt.utcoffset().total_seconds() - dt.utcoffset().total_seconds()) / 3600
            }
            
        except Exception as e:
            logger.error(f"Timezone conversion failed: {e}")
            return {'error': str(e)}
    
    def schedule_event(
        self,
        title: str,
        start_time: str,
        duration_minutes: Optional[int] = None,
        end_time: Optional[str] = None,
        timezone_str: str = 'UTC',
        event_type: str = 'reminder',
        description: str = '',
        priority: int = 3,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Schedule a time-based event"""
        try:
            event_id = f"event_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Parse start time
            start_dt = date_parser.parse(start_time)
            if start_dt.tzinfo is None:
                tz = pytz.timezone(self.timezones.get(timezone_str, timezone_str))
                start_dt = tz.localize(start_dt)
            
            # Calculate end time
            end_dt = None
            if end_time:
                end_dt = date_parser.parse(end_time)
                if end_dt.tzinfo is None:
                    tz = pytz.timezone(self.timezones.get(timezone_str, timezone_str))
                    end_dt = tz.localize(end_dt)
            elif duration_minutes:
                end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            # Create event
            event = TimeEvent(
                id=event_id,
                title=title,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                timezone=timezone_str,
                event_type=event_type,
                priority=priority,
                metadata=metadata or {}
            )
            
            # Store event
            self.events[event_id] = event
            
            return {
                'event_id': event_id,
                'title': title,
                'start_time': start_dt.isoformat(),
                'end_time': end_dt.isoformat() if end_dt else None,
                'timezone': timezone_str,
                'type': event_type,
                'priority': priority,
                'created': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Event scheduling failed: {e}")
            return {'error': str(e)}
    
    def get_upcoming_events(
        self,
        hours_ahead: int = 24,
        event_type: Optional[str] = None,
        min_priority: int = 1
    ) -> Dict[str, Any]:
        """Get upcoming events within specified time window"""
        try:
            current_time = datetime.utcnow()
            end_time = current_time + timedelta(hours=hours_ahead)
            
            upcoming = []
            
            for event in self.events.values():
                # Convert event time to UTC for comparison
                event_utc = event.start_time.astimezone(pytz.UTC).replace(tzinfo=None)
                
                # Check if event is within time window
                if current_time <= event_utc <= end_time:
                    # Apply filters
                    if event_type and event.event_type != event_type:
                        continue
                    if event.priority < min_priority:
                        continue
                    
                    # Calculate time until event
                    time_until = event_utc - current_time
                    
                    upcoming.append({
                        'event_id': event.id,
                        'title': event.title,
                        'description': event.description,
                        'start_time': event.start_time.isoformat(),
                        'end_time': event.end_time.isoformat() if event.end_time else None,
                        'timezone': event.timezone,
                        'type': event.event_type,
                        'priority': event.priority,
                        'time_until_hours': time_until.total_seconds() / 3600,
                        'time_until_minutes': time_until.total_seconds() / 60,
                        'metadata': event.metadata
                    })
            
            # Sort by start time
            upcoming.sort(key=lambda x: x['start_time'])
            
            return {
                'upcoming_events': upcoming,
                'count': len(upcoming),
                'time_window_hours': hours_ahead,
                'filters': {
                    'event_type': event_type,
                    'min_priority': min_priority
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get upcoming events: {e}")
            return {'error': str(e)}
    
    def is_market_open(self, exchange: str = 'NYSE') -> Dict[str, Any]:
        """Check if a specific market is currently open"""
        try:
            if exchange not in self.market_hours:
                return {'error': f'Unknown exchange: {exchange}'}
            
            market_config = self.market_hours[exchange]
            
            # Crypto markets are always open
            if market_config.get('always_open'):
                return {
                    'exchange': exchange,
                    'is_open': True,
                    'always_open': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get current time in market timezone
            market_tz = pytz.timezone(market_config['timezone'])
            current_time = datetime.now(market_tz)
            
            # Parse market hours
            open_time = datetime.strptime(market_config['open'], '%H:%M').time()
            close_time = datetime.strptime(market_config['close'], '%H:%M').time()
            
            # Check if market is open (Monday = 0, Sunday = 6)
            is_weekend = current_time.weekday() >= 5
            current_time_only = current_time.time()
            
            is_open = not is_weekend and open_time <= current_time_only <= close_time
            
            # Calculate time until next open/close
            next_action_time = None
            next_action = None
            
            if is_open:
                # Market is open, calculate time until close
                close_datetime = datetime.combine(current_time.date(), close_time)
                close_datetime = market_tz.localize(close_datetime)
                time_until = (close_datetime - current_time).total_seconds() / 60
                next_action = 'close'
                next_action_time = close_datetime.isoformat()
            else:
                # Market is closed, calculate time until open
                if current_time_only > close_time or is_weekend:
                    # Next business day
                    days_until_monday = (7 - current_time.weekday()) % 7
                    if days_until_monday == 0 and current_time_only > close_time:
                        days_until_monday = 1
                    next_open_date = current_time.date() + timedelta(days=days_until_monday or 1)
                else:
                    # Today before market open
                    next_open_date = current_time.date()
                
                open_datetime = datetime.combine(next_open_date, open_time)
                open_datetime = market_tz.localize(open_datetime)
                time_until = (open_datetime - current_time).total_seconds() / 60
                next_action = 'open'
                next_action_time = open_datetime.isoformat()
            
            return {
                'exchange': exchange,
                'is_open': is_open,
                'current_time': current_time.isoformat(),
                'market_timezone': market_config['timezone'],
                'open_time': market_config['open'],
                'close_time': market_config['close'],
                'next_action': next_action,
                'next_action_time': next_action_time,
                'minutes_until_next_action': round(time_until, 2),
                'is_weekend': is_weekend,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market status check failed for {exchange}: {e}")
            return {'error': str(e)}
    
    def get_trading_sessions(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Get trading sessions for all major markets"""
        try:
            if date_str:
                target_date = date_parser.parse(date_str).date()
            else:
                target_date = datetime.utcnow().date()
            
            sessions = {}
            
            for exchange, config in self.market_hours.items():
                if config.get('always_open'):
                    sessions[exchange] = {
                        'exchange': exchange,
                        'always_open': True,
                        'timezone': config['timezone']
                    }
                    continue
                
                # Calculate session times in UTC
                market_tz = pytz.timezone(config['timezone'])
                
                open_datetime = datetime.combine(target_date, datetime.strptime(config['open'], '%H:%M').time())
                open_datetime = market_tz.localize(open_datetime).astimezone(pytz.UTC)
                
                close_datetime = datetime.combine(target_date, datetime.strptime(config['close'], '%H:%M').time())
                close_datetime = market_tz.localize(close_datetime).astimezone(pytz.UTC)
                
                sessions[exchange] = {
                    'exchange': exchange,
                    'date': target_date.isoformat(),
                    'open_utc': open_datetime.isoformat(),
                    'close_utc': close_datetime.isoformat(),
                    'open_local': open_datetime.astimezone(market_tz).isoformat(),
                    'close_local': close_datetime.astimezone(market_tz).isoformat(),
                    'timezone': config['timezone'],
                    'duration_hours': (close_datetime - open_datetime).total_seconds() / 3600
                }
            
            return {
                'date': target_date.isoformat(),
                'sessions': sessions,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get trading sessions: {e}")
            return {'error': str(e)}
    
    def calculate_time_difference(
        self,
        start_time: str,
        end_time: str,
        unit: str = 'minutes'
    ) -> Dict[str, Any]:
        """Calculate time difference between two timestamps"""
        try:
            start_dt = date_parser.parse(start_time)
            end_dt = date_parser.parse(end_time)
            
            # Calculate difference
            diff = end_dt - start_dt
            total_seconds = diff.total_seconds()
            
            units = {
                'seconds': total_seconds,
                'minutes': total_seconds / 60,
                'hours': total_seconds / 3600,
                'days': diff.days,
                'weeks': diff.days / 7
            }
            
            return {
                'start_time': start_time,
                'end_time': end_time,
                'difference': {
                    'seconds': round(units['seconds'], 2),
                    'minutes': round(units['minutes'], 2),
                    'hours': round(units['hours'], 2),
                    'days': units['days'],
                    'weeks': round(units['weeks'], 2)
                },
                'requested_unit': unit,
                'value_in_unit': round(units.get(unit, units['minutes']), 2),
                'is_future': total_seconds > 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Time difference calculation failed: {e}")
            return {'error': str(e)}
    
    def get_business_days(
        self,
        start_date: str,
        end_date: str,
        exclude_weekends: bool = True,
        holidays: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculate business days between two dates"""
        try:
            start_dt = date_parser.parse(start_date).date()
            end_dt = date_parser.parse(end_date).date()
            
            # Parse holidays
            holiday_dates = set()
            if holidays:
                for holiday in holidays:
                    holiday_dates.add(date_parser.parse(holiday).date())
            
            business_days = 0
            current_date = start_dt
            dates_list = []
            
            while current_date <= end_dt:
                is_weekend = current_date.weekday() >= 5
                is_holiday = current_date in holiday_dates
                
                if not (exclude_weekends and is_weekend) and not is_holiday:
                    business_days += 1
                    dates_list.append(current_date.isoformat())
                
                current_date += timedelta(days=1)
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'business_days': business_days,
                'total_days': (end_dt - start_dt).days + 1,
                'exclude_weekends': exclude_weekends,
                'holidays_count': len(holiday_dates),
                'business_dates': dates_list,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business days calculation failed: {e}")
            return {'error': str(e)}
    
    def format_duration(self, seconds: float) -> Dict[str, Any]:
        """Format duration in human-readable format"""
        try:
            td = timedelta(seconds=seconds)
            
            days = td.days
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Create human readable format
            parts = []
            if days:
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            if hours:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if seconds:
                parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
            human_readable = ", ".join(parts) if parts else "0 seconds"
            
            return {
                'total_seconds': seconds,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'human_readable': human_readable,
                'iso_format': str(td),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Duration formatting failed: {e}")
            return {'error': str(e)}


# Global instance
time_mcp = TimeMCPAdapter()


# MCP-compatible interface functions
async def mcp_get_current_time(timezone_str: str = 'UTC') -> Dict[str, Any]:
    """MCP-compatible current time retrieval"""
    return time_mcp.get_current_time(timezone_str)


async def mcp_convert_timezone(
    datetime_str: str,
    from_timezone: str,
    to_timezone: str
) -> Dict[str, Any]:
    """MCP-compatible timezone conversion"""
    return time_mcp.convert_timezone(datetime_str, from_timezone, to_timezone)


async def mcp_schedule_event(
    title: str,
    start_time: str,
    **kwargs
) -> Dict[str, Any]:
    """MCP-compatible event scheduling"""
    return time_mcp.schedule_event(title, start_time, **kwargs)


async def mcp_get_upcoming_events(**kwargs) -> Dict[str, Any]:
    """MCP-compatible upcoming events retrieval"""
    return time_mcp.get_upcoming_events(**kwargs)


async def mcp_is_market_open(exchange: str = 'NYSE') -> Dict[str, Any]:
    """MCP-compatible market status check"""
    return time_mcp.is_market_open(exchange)


async def mcp_get_trading_sessions(date_str: Optional[str] = None) -> Dict[str, Any]:
    """MCP-compatible trading sessions retrieval"""
    return time_mcp.get_trading_sessions(date_str)