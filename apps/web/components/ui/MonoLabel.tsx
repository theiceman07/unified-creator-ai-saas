export function MonoLabel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`font-mono text-label text-ink-500 ${className}`}>
      ({children})
    </span>
  );
}
