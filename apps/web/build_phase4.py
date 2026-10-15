import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# --- 1. Basic Components ---
write_file('components/ui/MonoLabel.tsx', """
export function MonoLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-label text-ink-500">
      ({children})
    </span>
  );
}
""")

write_file('components/ui/Hairline.tsx', """
export function Hairline() {
  return <hr className="border-t hairline border-ink-700 w-full" />;
}
""")

write_file('components/ui/StatusDot.tsx', """
export function StatusDot({ live }: { live?: boolean }) {
  return (
    <span className={`inline-block w-2 h-2 rounded-full ${live ? 'bg-signal-live animate-pulse' : 'bg-ink-500'}`} />
  );
}
""")

write_file('components/ui/JudgeBadge.tsx', """
export function JudgeBadge({ score, critique }: { score: number, critique?: string }) {
  const signal = score >= 4.0 ? 'text-signal-pass' : score >= 3.0 ? 'text-signal-warn' : 'text-signal-fail';
  return (
    <span className={`font-mono text-label border hairline border-ink-700 rounded-sm px-1 py-0.5 ${signal}`} title={critique}>
      {score.toFixed(1)}
    </span>
  );
}
""")

write_file('components/ui/OriginChip.tsx', """
import Link from 'next/link';

export function OriginChip({ projectId }: { projectId: string }) {
  return (
    <Link href="/system" className="font-mono text-label text-ink-500 hover:text-paper-100 transition-colors">
      #{projectId}
    </Link>
  );
}
""")

write_file('components/ui/PaperSurface.tsx', """
export function PaperSurface({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`paper-surface rounded-md p-4 hairline border-paper-400 ${className}`}>
      {children}
    </div>
  );
}
""")

write_file('components/ui/Button.tsx', """
export function Button({ variant = 'primary', children, ...props }: any) {
  const base = "px-4 py-2 rounded-sm text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-paper-100 focus:ring-offset-2 focus:ring-offset-ink-900";
  const variants = {
    primary: "bg-paper-100 text-ink-900 hover:bg-paper-200",
    secondary: "bg-transparent text-paper-100 hairline border-ink-700 hover:bg-ink-800",
    text: "bg-transparent text-paper-100 hover:underline"
  };
  return (
    <button className={`${base} ${variants[variant as keyof typeof variants]}`} {...props}>
      {children}
    </button>
  );
}
""")

# --- 2. Kitchen Sink Route ---
write_file('app/dev/kitchen-sink/page.tsx', """
import { MonoLabel } from "@/components/ui/MonoLabel";
import { Hairline } from "@/components/ui/Hairline";
import { StatusDot } from "@/components/ui/StatusDot";
import { JudgeBadge } from "@/components/ui/JudgeBadge";
import { OriginChip } from "@/components/ui/OriginChip";
import { PaperSurface } from "@/components/ui/PaperSurface";
import { Button } from "@/components/ui/Button";

export default function KitchenSink() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-12">
      <h1 className="text-h2 font-display">Design System Kitchen Sink</h1>
      
      <section className="space-y-4">
        <h2 className="text-h4">Colors & Themes</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="theme-dark p-6 rounded-md">
            <h3 className="text-text-lg mb-2">Dark Theme (Default Chrome)</h3>
            <p className="text-ink-400 text-sm">Text is paper-100, background is ink-900.</p>
          </div>
          <div className="theme-light p-6 rounded-md hairline">
            <h3 className="text-text-lg mb-2">Light Theme</h3>
            <p className="text-ink-600 text-sm">Text is ink-900, background is paper-300.</p>
          </div>
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-h4">Typography</h2>
        <div className="space-y-2">
          <div className="text-display">Display</div>
          <div className="text-h1">Heading 1</div>
          <div className="text-h2">Heading 2</div>
          <div className="text-h3">Heading 3</div>
          <div className="text-h4">Heading 4</div>
          <div className="text-text-lg">Large Text Body</div>
          <div className="text-text">Regular Text Body</div>
          <div className="text-text-sm">Small Text</div>
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-h4">Components</h2>
        <div className="flex flex-wrap gap-4 items-center">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="text">Text Link</Button>
          <MonoLabel>parenthetical label</MonoLabel>
          <StatusDot live={true} />
          <StatusDot />
          <JudgeBadge score={4.8} critique="Excellent" />
          <JudgeBadge score={3.2} critique="Needs work" />
          <JudgeBadge score={2.1} critique="Poor" />
          <OriginChip projectId="09" />
        </div>
        <div className="mt-4">
          <Hairline />
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-h4">Paper Surface (Writing Area)</h2>
        <PaperSurface>
          <h3 className="text-text-lg mb-2">Generated Script</h3>
          <p className="text-text">
            This is what generated content looks like. It sits on a paper-200 surface with ink-900 text,
            resembling a real document against the dark chrome of the app.
          </p>
        </PaperSurface>
      </section>
    </div>
  );
}
""")

print("Phase 4 components and kitchen sink generated.")
