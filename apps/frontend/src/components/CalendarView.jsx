// Calendar view - scheduled events

import { useState, useEffect } from 'react';
import api from '../services/api';
import { formatTimestamp } from '../utils/time';

export default function CalendarView() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCalendar = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCalendar('default');
      setEvents(data.events || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load calendar:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCalendar();
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadCalendar, 10000);
    return () => clearInterval(interval);
  }, []);

  // Parse ical_data to extract recurrence and start time
  const parseIcalData = (icalData) => {
    try {
      // Extract recurrence
      const rruleMatch = icalData.match(/RRULE:FREQ=([A-Z]+)/);
      const recurrence = rruleMatch ? rruleMatch[1].toLowerCase() : null;

      // Extract start time
      const dtstartMatch = icalData.match(/DTSTART:(\d{8}T\d{6})/);
      let startTime = null;
      if (dtstartMatch) {
        const dtStr = dtstartMatch[1];
        // Parse YYYYMMDDTHHMMSS
        const year = dtStr.substring(0, 4);
        const month = dtStr.substring(4, 6);
        const day = dtStr.substring(6, 8);
        const hour = dtStr.substring(9, 11);
        const minute = dtStr.substring(11, 13);
        startTime = new Date(`${year}-${month}-${day}T${hour}:${minute}`);
      }

      return { recurrence, startTime };
    } catch {
      return { recurrence: null, startTime: null };
    }
  };

  if (loading && events.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Loading calendar...
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-950 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Calendar</h2>
        <p className="text-gray-400">
          Scheduled events and tasks
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <div className="flex-1 overflow-auto">
        {events.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            No events scheduled
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => {
              const { recurrence, startTime } = parseIcalData(event.ical_data);
              const recurrenceLabel = recurrence ? ` (${recurrence})` : ' (one-time)';

              // Event title: responsibility title or event title
              const title = event.responsibility_title || event.title || 'Untitled event';
              const details = event.responsibility_id
                ? event.responsibility_description
                : event.description;

              return (
                <div
                  key={event.id}
                  className="bg-gray-900 rounded-lg p-4 border border-gray-800 hover:border-gray-700 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-100">
                      {title}
                    </h3>
                    <span className="text-sm text-blue-400 font-mono">
                      #{event.id}
                    </span>
                  </div>

                  {details && (
                    <p className="text-gray-300 text-sm mb-3">
                      {details}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-4 text-sm">
                    {startTime && (
                      <span className="text-yellow-400">
                        Start: {startTime.toLocaleString()}
                      </span>
                    )}
                    <span className="text-purple-400">
                      {recurrenceLabel}
                    </span>
                    {event.responsibility_id && (
                      <a
                        href="#responsibilities"
                        onClick={(e) => {
                          e.preventDefault();
                          // Navigate to responsibilities tab
                          const tabButton = document.querySelector('[data-tab-id="responsibilities"]');
                          if (tabButton) tabButton.click();
                        }}
                        className="text-green-400 hover:text-green-300 underline cursor-pointer"
                      >
                        → Responsibility #{event.responsibility_id}
                      </a>
                    )}
                  </div>

                  <div className="mt-3 flex gap-4 text-xs text-gray-500">
                    <span title={new Date(event.created_at).toLocaleString()}>
                      Created {formatTimestamp(event.created_at)}
                    </span>
                    <span title={new Date(event.updated_at).toLocaleString()}>
                      Updated {formatTimestamp(event.updated_at)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="mt-4 text-sm text-gray-500">
        {events.length} {events.length === 1 ? 'event' : 'events'} • Auto-refreshes every 10 seconds
      </div>
    </div>
  );
}
