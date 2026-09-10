export default function LoadingState({ label }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-spotify-card p-10 text-center text-spotify-muted">
      {label}…
    </div>
  );
}
