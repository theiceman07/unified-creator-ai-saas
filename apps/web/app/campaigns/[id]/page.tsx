'use client';
import { useRunStream } from '@/lib/useRunStream';
import { MonoLabel } from '@/components/ui/MonoLabel';
import { AiCard } from '@/components/cards/AiCard';

export default function CampaignPage({ params }: { params: { id: string } }) {
  const { events } = useRunStream(params.id);
  
  // Extract final assets and cards from events
  const cards = events.filter(e => e.type === 'card_yielded').map(e => e.data);
  const isFinished = events.some(e => e.type === 'finished');
  
  return (
    <div className="theme-dark min-h-screen flex">
      {/* Sidebar stub */}
      <div className="w-64 border-r hairline border-ink-700 p-4">
        <h2 className="text-h4">Campaign</h2>
        <MonoLabel>status: {isFinished ? 'completed' : 'running'}</MonoLabel>
      </div>
      
      {/* Main Workspace */}
      <div className="flex-1 p-8">
        <div className="max-w-3xl mx-auto space-y-8">
          <h1 className="text-h2">AI agents for beginner developers</h1>
          
          <div className="space-y-6">
            {cards.map((card, i) => (
              <AiCard 
                key={i} 
                kind={card.kind} 
                score={card.judge_score} 
                critique={card.judge_critique}
              >
                <pre className="text-sm overflow-x-auto whitespace-pre-wrap">{JSON.stringify(card.data, null, 2)}</pre>
              </AiCard>
            ))}
            
            {!isFinished && (
              <div className="text-ink-500 animate-pulse font-mono text-sm border hairline border-ink-700 p-4 rounded-sm">
                Agent is thinking...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
