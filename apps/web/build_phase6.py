import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- 1. Card Shell & Registry ---
write_file('components/cards/registry.ts', """
import { FC } from 'react';

export const CardRegistry: Record<string, FC<any>> = {
  // Add specific cards here e.g. 'research_brief': ResearchCard
};
""")

write_file('components/cards/AiCard.tsx', """
import { JudgeBadge } from '../ui/JudgeBadge';
import { OriginChip } from '../ui/OriginChip';
import { PaperSurface } from '../ui/PaperSurface';

interface AiCardProps {
  kind: string;
  data: any;
  score?: number;
  critique?: string;
  originId?: string;
  children: React.ReactNode;
}

export function AiCard({ kind, score, critique, originId, children }: AiCardProps) {
  return (
    <div className="flex flex-col gap-2 mb-6">
      <div className="flex justify-between items-center px-2">
        <div className="text-ink-500 font-mono text-sm capitalize">{kind.replace('_', ' ')}</div>
        <div className="flex items-center gap-3">
          {originId && <OriginChip projectId={originId} />}
          {score && <JudgeBadge score={score} critique={critique} />}
        </div>
      </div>
      <PaperSurface>
        {children}
      </PaperSurface>
    </div>
  );
}
""")

# --- 2. useRunStream Hook ---
write_file('lib/useRunStream.ts', """
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
""")

# --- 3. Home Route ---
write_file('app/home/page.tsx', """
import { MonoLabel } from '@/components/ui/MonoLabel';

export default function Home() {
  return (
    <div className="theme-dark min-h-screen p-8 max-w-5xl mx-auto flex flex-col gap-12">
      <div>
        <MonoLabel>thursday · 09:12</MonoLabel>
        <h1 className="text-display-sm font-display tracking-tight mt-4">Good morning, Creator.</h1>
      </div>
      
      <div className="bg-paper-200 text-ink-900 rounded-md p-6 text-xl">
        <input 
          type="text" 
          placeholder="What are you thinking about?_" 
          className="bg-transparent outline-none w-full placeholder-ink-500"
        />
      </div>
      
      <div>
        <MonoLabel>today's opportunities</MonoLabel>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          <div className="border-l hairline border-ink-700 pl-4">
            <h3 className="text-h4">AI agents for beginners</h3>
            <p className="text-ink-500 text-sm mt-2">Trending topic (potential 82)</p>
            <button className="text-paper-100 hover:underline text-sm mt-4">Create campaign</button>
          </div>
          <div className="border-l hairline border-ink-700 pl-4">
            <h3 className="text-h4">"Agent vs chatbot?"</h3>
            <p className="text-ink-500 text-sm mt-2">From your audience (asked 14 times)</p>
            <button className="text-paper-100 hover:underline text-sm mt-4">Create campaign</button>
          </div>
        </div>
      </div>
    </div>
  );
}
""")

# --- 4. Campaign Route ---
write_file('app/campaigns/[id]/page.tsx', """
'use client';
import { useRunStream } from '@/lib/useRunStream';
import { MonoLabel } from '@/components/ui/MonoLabel';

export default function CampaignPage({ params }: { params: { id: string } }) {
  const { events } = useRunStream(params.id);
  
  return (
    <div className="theme-dark min-h-screen flex">
      {/* Sidebar stub */}
      <div className="w-64 border-r hairline border-ink-700 p-4">
        <h2 className="text-h4">Campaign</h2>
        <MonoLabel>status: running</MonoLabel>
      </div>
      
      {/* Main Workspace */}
      <div className="flex-1 p-8">
        <div className="max-w-3xl mx-auto space-y-8">
          <h1 className="text-h2">AI agents for beginner developers</h1>
          
          <div className="space-y-4">
            {events.map((e, i) => (
              <div key={i} className="p-4 border hairline border-ink-700 rounded-sm">
                <MonoLabel>{e.type}</MonoLabel>
                <pre className="text-sm mt-2 overflow-x-auto">{JSON.stringify(e.data, null, 2)}</pre>
              </div>
            ))}
            {events.length === 0 && <div className="text-ink-500">Waiting for agent execution...</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
""")

print("Phase 6 app UI generated.")
