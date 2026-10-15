export function JudgeBadge({ score, critique }: { score: number, critique?: string }) {
  const signal = score >= 4.0 ? 'text-signal-pass' : score >= 3.0 ? 'text-signal-warn' : 'text-signal-fail';
  return (
    <span className={`font-mono text-label border hairline border-ink-700 rounded-sm px-1 py-0.5 ${signal}`} title={critique}>
      {score.toFixed(1)}
    </span>
  );
}
