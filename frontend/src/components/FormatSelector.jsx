function formatSize(bytes) {
  if (!bytes) return null;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FormatSelector({ formats, selected, onSelect }) {
  return (
    <div className="card">
      <p className="text-sm text-gray-400 font-medium mb-3">Formato de download:</p>
      <div className="grid gap-2">
        {formats.map((fmt) => {
          const isSelected = selected?.format_id === fmt.format_id;
          return (
            <button
              key={fmt.format_id}
              onClick={() => onSelect(fmt)}
              className={`flex items-center justify-between px-4 py-2.5 rounded-xl border
                text-sm transition-all duration-150 text-left w-full ${
                isSelected
                  ? "border-blue-500 bg-blue-900/30 text-white"
                  : "border-gray-700 bg-gray-800/40 text-gray-300 hover:border-gray-500"
              }`}
            >
              <span className="flex items-center gap-2.5">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  isSelected ? "bg-blue-400" : "bg-gray-600"
                }`} />
                {fmt.label}
              </span>
              {fmt.filesize && (
                <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                  ~{formatSize(fmt.filesize)}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}