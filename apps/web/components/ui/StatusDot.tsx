export function StatusDot({ live }: { live?: boolean }) {
  return (
    <span className={`inline-block w-2 h-2 rounded-full ${live ? 'bg-signal-live animate-pulse' : 'bg-ink-500'}`} />
  );
}
