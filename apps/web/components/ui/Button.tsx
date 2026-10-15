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
