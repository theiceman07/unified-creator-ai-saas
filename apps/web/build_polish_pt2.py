import os

def write_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

write_file('app/page.tsx', """
import { MonoLabel } from '@/components/ui/MonoLabel';

export default function Home() {
  return (
    <div className="theme-dark min-h-screen">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center text-center p-24 bg-gradient-to-b from-ink-900 to-ink-800">
        <MonoLabel className="animate-pulse">v1.0 is live</MonoLabel>
        <h1 className="text-display font-display mt-8 mb-6 bg-clip-text text-transparent bg-gradient-to-r from-paper-100 to-ink-400">
          CreatorOS
        </h1>
        <p className="text-h3 text-ink-300 max-w-2xl">
          The ultimate orchestration layer for your content empire.
        </p>
        <button className="mt-12 px-8 py-4 bg-paper-100 text-ink-900 font-bold rounded-full hover:bg-paper-200 transition-all transform hover:scale-105 shadow-xl hover:shadow-2xl">
          Enter Workspace
        </button>
      </div>

      {/* 27 Projects Grid */}
      <div className="p-24 bg-paper-100 theme-light">
        <h2 className="text-h2 text-ink-900 font-display mb-12 text-center">27 Agent Workflows</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-8 border hairline border-ink-300 rounded-2xl hover:border-ink-500 transition-colors bg-paper-200">
              <div className="w-12 h-12 bg-ink-900 rounded-full mb-6 text-paper-100 flex items-center justify-center font-mono">0{i}</div>
              <h3 className="text-h3 mb-4">Autopilot Loop</h3>
              <p className="text-ink-500">Autonomous content generation running weekly.</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
""")

print("UI Polish Pt2 applied (Landing page glow up).")
