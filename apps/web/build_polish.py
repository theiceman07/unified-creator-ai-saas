import os

def write_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

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
""")

write_file('tailwind.config.ts', """
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.5s ease-out',
      }
    },
  },
  plugins: [],
};
export default config;
""")

print("UI Polish applied (AiCard micro-animations and Tailwind config updated).")
