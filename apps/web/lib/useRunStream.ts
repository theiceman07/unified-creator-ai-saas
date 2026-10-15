import { useState, useEffect } from 'react';

export function useRunStream(runId: string) {
  const [events, setEvents] = useState<any[]>([]);
  
  useEffect(() => {
    if (!runId) return;
    
    const es = new EventSource(`http://localhost:8000/v1/runs/${runId}/events`);
    
    es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, { type: event.type, data }]);
    };
    
    return () => es.close();
  }, [runId]);
  
  return { events };
}
