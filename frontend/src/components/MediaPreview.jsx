function formatDuration(seconds) {
  if (!seconds) return null;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function MediaPreview({ info }) {
  const duration = formatDuration(info.duration);

  return (
    <div className="card flex gap-4 items-start">
      {info.thumbnail && (
        <img
          src={info.thumbnail}
          alt={info.title}
          className="w-28 h-18 object-cover rounded-lg flex-shrink-0 bg-gray-800"
          onError={(e) => { e.target.style.display = "none"; }}
        />
      )}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-sm leading-snug line-clamp-2">
          {info.title}
        </h3>
        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-gray-400">
          <span>{info.uploader}</span>
          {duration && <span>⏱ {duration}</span>}
          {info.platform && (
            <span className="text-blue-400 font-medium">{info.platform}</span>
          )}
        </div>
      </div>
    </div>
  );
}