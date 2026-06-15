export default function URLInput({ url, onChange, onSubmit, loading }) {
  return (
    <div className="flex flex-col sm:flex-row gap-2">
      <input
        type="url"
        value={url}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSubmit()}
        placeholder="Cole a URL do vídeo aqui..."
        className="input-url flex-1"
        disabled={loading}
        autoFocus
      />
      <button
        onClick={onSubmit}
        disabled={loading || !url.trim()}
        className="btn-primary sm:w-auto sm:px-8"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10"
                stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Buscando...
          </span>
        ) : (
          "Buscar"
        )}
      </button>
    </div>
  );
}