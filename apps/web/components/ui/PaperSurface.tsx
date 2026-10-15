export function PaperSurface({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`paper-surface rounded-md p-4 hairline border-paper-400 ${className}`}>
      {children}
    </div>
  );
}
