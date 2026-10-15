import Link from 'next/link';

export function OriginChip({ projectId }: { projectId: string }) {
  return (
    <Link href="/system" className="font-mono text-label text-ink-500 hover:text-paper-100 transition-colors">
      #{projectId}
    </Link>
  );
}
