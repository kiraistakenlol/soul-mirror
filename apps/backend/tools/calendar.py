# Calendar manager - wraps icalendar library complexity
from repository.calendar import CalendarRepository
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from recurring_ical_events import of
from typing import Optional
import pytz

class CalendarManager:
    """Manages calendar events using icalendar library"""

    def __init__(self):
        self.repo = CalendarRepository()

    def _create_ical_event(self, start_time: datetime, recurrence: Optional[str]) -> str:
        """Create iCalendar VEVENT and serialize to string"""
        cal = Calendar()
        cal.add('prodid', '-//Soul Mirror//Calendar//EN')
        cal.add('version', '2.0')

        event = Event()
        event.add('dtstart', start_time)
        event.add('dtstamp', datetime.now(pytz.UTC))
        event.add('uid', f"{datetime.now().timestamp()}@soulmirror")

        # Add recurrence rule if specified
        if recurrence:
            recurrence_map = {
                'daily': {'freq': 'daily'},
                'weekly': {'freq': 'weekly'},
                'monthly': {'freq': 'monthly'},
                'yearly': {'freq': 'yearly'}
            }
            if recurrence.lower() in recurrence_map:
                event.add('rrule', recurrence_map[recurrence.lower()])

        cal.add_component(event)
        return cal.to_ical().decode('utf-8')

    def _parse_ical_event(self, ical_data: str) -> dict:
        """Parse iCalendar data and extract event details"""
        cal = Calendar.from_ical(ical_data)
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get('dtstart').dt
                rrule = component.get('rrule')

                # Extract recurrence type
                recurrence = None
                if rrule:
                    freq = rrule.get('FREQ', [None])[0]
                    if freq:
                        recurrence = freq.lower()

                return {
                    'start_time': dtstart,
                    'recurrence': recurrence
                }
        return None

    def _get_next_occurrence(self, ical_data: str, after: datetime = None) -> Optional[datetime]:
        """Get next occurrence of event after given time (or now)"""
        if after is None:
            after = datetime.now()

        try:
            cal = Calendar.from_ical(ical_data)
            # Get occurrences in next year (far enough to find next one)
            occurrences = of(cal).between(after, after + timedelta(days=365))
            return occurrences[0] if occurrences else None
        except Exception as e:
            print(f"❌ Error getting next occurrence: {e}")
            return None

    def add_event(self, user_id: str, scheduled_time: str,
                  recurrence: Optional[str] = None,
                  responsibility_id: Optional[int] = None,
                  title: Optional[str] = None,
                  description: Optional[str] = None) -> str:
        """Add calendar event for a responsibility or one-time task"""
        try:
            # Parse scheduled time
            dt = datetime.fromisoformat(scheduled_time)

            # Create iCalendar event
            ical_data = self._create_ical_event(dt, recurrence)

            # Store event
            event_id = self.repo.create_event(
                user_id=user_id,
                ical_data=ical_data,
                responsibility_id=responsibility_id,
                title=title,
                description=description
            )

            recurrence_info = f" ({recurrence})" if recurrence else " (one-time)"
            event_type = f"responsibility #{responsibility_id}" if responsibility_id else f"'{title or description}'"
            print(f"📅 Created calendar event id={event_id} for {event_type} at {dt}{recurrence_info}")
            return f"Scheduled event #{event_id} for {dt.strftime('%Y-%m-%d %H:%M')}{recurrence_info}"

        except Exception as e:
            print(f"❌ Error creating calendar event: {e}")
            return f"Error: {str(e)}"

    def list_events(self, user_id: str) -> str:
        """List all calendar events for user with next occurrence"""
        try:
            events = self.repo.get_all_events(user_id)

            if not events:
                return "No calendar events scheduled."

            lines = ["Calendar Events:"]
            for event in events:
                # Parse ical to get recurrence info and next occurrence
                parsed = self._parse_ical_event(event['ical_data'])
                next_occurrence = self._get_next_occurrence(event['ical_data'])

                recurrence_info = f" ({parsed['recurrence']})" if parsed['recurrence'] else " (one-time)"

                # Event title: use responsibility title or event title
                title = event['responsibility_title'] if event['responsibility_id'] else event['title']

                next_info = next_occurrence.strftime('%Y-%m-%d %H:%M') if next_occurrence else "no future occurrences"

                lines.append(
                    f"#{event['id']}: {title} - next: {next_info}{recurrence_info}"
                )

            return "\n".join(lines)

        except Exception as e:
            print(f"❌ Error listing events: {e}")
            return f"Error: {str(e)}"

    def remove_event(self, user_id: str, event_id: int) -> str:
        """Remove calendar event"""
        try:
            success = self.repo.delete_event(user_id, event_id)
            if success:
                print(f"🗑️  Deleted calendar event id={event_id}")
                return f"Removed event #{event_id}"
            else:
                return f"Event #{event_id} not found"

        except Exception as e:
            print(f"❌ Error removing event: {e}")
            return f"Error: {str(e)}"

    def get_events_due(self, user_id: str, within_seconds: int = 10) -> list:
        """Get events that should trigger within specified seconds from now"""
        try:
            now = datetime.now()
            check_until = now + timedelta(seconds=within_seconds)

            all_events = self.repo.get_all_events(user_id)
            due_events = []

            for event in all_events:
                # Get occurrences within check window
                cal = Calendar.from_ical(event['ical_data'])
                occurrences = of(cal).between(now, check_until)

                if occurrences:
                    # Add event with its next occurrence time
                    event['next_occurrence'] = occurrences[0]
                    due_events.append(event)

            return due_events

        except Exception as e:
            print(f"❌ Error getting due events: {e}")
            return []


# Global singleton
calendar_manager = CalendarManager()
