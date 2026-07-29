export default function ErrorBanner({ message }) {
  if (!message) return null;

  return (
    <div className="mt-8 border-l-2 border-red-700/70 bg-red-700/5 py-3 pl-4 pr-4">
      <p className="text-xs font-medium uppercase tracking-wide text-red-800">Something went wrong</p>
      <p className="mt-1 text-sm text-red-900/80">{message}</p>
    </div>
  );
}
