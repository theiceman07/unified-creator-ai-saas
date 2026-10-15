import Link from 'next/link';
import { MonoLabel } from '@/components/ui/MonoLabel';

export default function NotFound() {
  return (
    <div className="theme-dark min-h-screen flex flex-col items-center justify-center p-8">
      <h2 className="text-display font-display mb-4 opacity-50">404</h2>
      <p className="text-text-lg text-ink-500 mb-8">This module doesn't exist in the CreatorOS registry.</p>
      <Link href="/" className="px-6 py-3 bg-transparent text-paper-100 border hairline border-ink-700 hover:bg-ink-800 transition-colors">
        Return Home
      </Link>
    </div>
  );
}
