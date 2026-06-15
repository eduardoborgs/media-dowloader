import { useState } from "react";
import URLInput from "./components/URLInput";
import MediaPreview from "./components/MediaPreview";
import FormatSelector from "./components/FormatSelector";
import { fetchMediaInfo, buildDownloadUrl } from "./services/api";

export default function App() {
  const [url, setUrl] = useState("");
  const [mediaInfo, setMediaInfo] = useState(null);
  const [selectedFormat, setSelectedFormat] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  const handleFetch = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setMediaInfo(null);
    setSelectedFormat(null);

    try {
      const info = await fetchMediaInfo(url.trim());
      setMediaInfo(info);
      setSelectedFormat(info.formats[0] ?? null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!selectedFormat) return;
    setDownloading(true);

    const mediaType = selectedFormat.is_audio_only ? "audio" : "video";
    const downloadUrl = buildDownloadUrl(url, selectedFormat.format_id, mediaType);

    const link = document.createElement("a");
    link.href = downloadUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => setDownloading(false), 3000);
  };

  const handleReset = () => {
    setUrl("");
    setMediaInfo(null);
    setSelectedFormat(null);
    setError("");
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 py-4 px-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-blue-400">MediaGet</span>
          </div>
          <span className="text-xs text-gray-600 hidden sm:block">
            Apenas conteúdos permitidos
          </span>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-2xl w-full mx-auto px-4 py-10 space-y-4">
        <URLInput
          url={url}
          onChange={setUrl}
          onSubmit={handleFetch}
          loading={loading}
        />

        {error && (
          <div className="flex gap-2 p-4 bg-red-950/60 border border-red-800
                          rounded-xl text-sm text-red-300">
            <span className="flex-shrink-0">⚠</span>
            <span>{error}</span>
          </div>
        )}

        {mediaInfo && (
          <>
            <MediaPreview info={mediaInfo} />

            {mediaInfo.formats.length > 0 ? (
              <>
                <FormatSelector
                  formats={mediaInfo.formats}
                  selected={selectedFormat}
                  onSelect={setSelectedFormat}
                />
                <button
                  onClick={handleDownload}
                  disabled={downloading || !selectedFormat}
                  className="btn-primary"
                >
                  {downloading ? "Preparando download..." : "⬇ Baixar agora"}
                </button>
              </>
            ) : (
              <div className="card text-center text-gray-500 text-sm py-6">
                Nenhum formato disponível para este conteúdo.
              </div>
            )}

            <button
              onClick={handleReset}
              className="w-full py-2 text-sm text-gray-600 hover:text-gray-400
                         transition-colors"
            >
              ↩ Buscar outro vídeo
            </button>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-5 text-center">
        <p className="text-xs text-gray-700 max-w-sm mx-auto px-4">
          Use este serviço apenas para conteúdos que você tem permissão para baixar.
          Respeite os termos de uso das plataformas e os direitos autorais.
        </p>
      </footer>
    </div>
  );
}