'use client';
 
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="theme-dark min-h-screen flex flex-col items-center justify-center p-8">
        <h2 className="text-h2 font-display text-signal-fail mb-4">Something went critically wrong!</h2>
        <p className="text-ink-500 mb-8 font-mono">{error.message}</p>
        <button 
          onClick={() => reset()}
          className="px-6 py-3 bg-paper-100 text-ink-900 rounded-sm hover:bg-paper-200 transition-colors"
        >
          Try again
        </button>
      </body>
    </html>
  );
}
