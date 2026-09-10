export default function ErrorState({ message }) {
  return (
    <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-200">
      <p className="font-semibold">Could not load this view</p>
      <p className="mt-2 text-sm">{message}</p>
      <p className="mt-3 text-sm text-rose-200/80">
        Start the API on port 8000 and confirm <code>SPOTIFY_PARQUET_PATH</code> points at the clustered Parquet.
      </p>
    </div>
  );
}
