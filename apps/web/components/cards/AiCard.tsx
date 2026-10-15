import { JudgeBadge } from '../ui/JudgeBadge';
import { OriginChip } from '../ui/OriginChip';
import { PaperSurface } from '../ui/PaperSurface';

interface AiCardProps {
  kind: string;
  data?: any;
  score?: number;
  critique?: string;
  originId?: string;
  children: React.ReactNode;
}

export function AiCard({ kind, data, score, critique, originId, children }: AiCardProps) {
  return (
    <div className="flex flex-col gap-2 mb-6 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-xl group opacity-0 animate-fade-in-up" style={{ animationFillMode: 'forwards' }}>
      <div className="flex justify-between items-center px-2">
        <div className="text-ink-500 font-mono text-sm capitalize flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-signal-success animate-pulse"></span>
          {kind.replace('_', ' ')}
        </div>
        <div className="flex items-center gap-3 transition-opacity duration-300 group-hover:opacity-100">
          {originId && <OriginChip projectId={originId} />}
          {score && <JudgeBadge score={score} critique={critique} />}
        </div>
      </div>
      <PaperSurface className="border hairline border-transparent group-hover:border-ink-200 transition-colors">
        {children}
      </PaperSurface>
    </div>
  );
}
