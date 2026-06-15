import asyncio
import os
import uuid
from pathlib import Path
from typing import Tuple

import yt_dlp

from models.schemas import Format, MediaInfo
from utils.cleanup import ensure_temp_dir
from utils.validators import is_safe_url

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "300"))


class MediaDownloader:

    def _base_opts(self) -> dict:
        return {
            "quiet": True,
            "no_warnings": True,
            "no_color": True,
            # Configurações Anti-Bloqueio do YouTube
            "extractor_args": {
                "youtube": ["client=android,mweb"]
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }
    
    async def get_info(self, url: str) -> MediaInfo:
        if not is_safe_url(url):
            raise ValueError("URL inválida ou não permitida.")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_get_info, url)

    def _sync_get_info(self, url: str) -> MediaInfo:
        opts = {**self._base_opts(), "skip_download": True}

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                raw = ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as exc:
                raise ValueError(f"Não foi possível acessar esta URL: {exc}")

        if not raw:
            raise ValueError("Nenhuma informação encontrada.")

        return MediaInfo(
            title=raw.get("title", "Sem título"),
            thumbnail=raw.get("thumbnail"),
            duration=raw.get("duration"),
            uploader=raw.get("uploader", "Desconhecido"),
            platform=raw.get("extractor_key", ""),
            formats=self._parse_formats(raw),
        )

    def _parse_formats(self, info: dict) -> list[Format]:
        raw_formats = info.get("formats", [])
        result: list[Format] = []
        seen: set[str] = set()

        result.append(Format(
            format_id="bestvideo+bestaudio/best",
            ext="mp4",
            label="Melhor qualidade (MP4)",
            is_audio_only=False,
        ))

        combined = [
            f for f in raw_formats
            if f.get("vcodec") not in ("none", None)
            and f.get("acodec") not in ("none", None)
            and f.get("ext") in ("mp4", "webm")
            and f.get("height")
        ]
        combined.sort(key=lambda f: f.get("height", 0), reverse=True)

        for f in combined:
            label = f"{f.get('height')}p ({f.get('ext', 'mp4')})"
            if label not in seen:
                seen.add(label)
                result.append(Format(
                    format_id=f["format_id"],
                    ext=f.get("ext", "mp4"),
                    label=label,
                    filesize=f.get("filesize") or f.get("filesize_approx"),
                    is_audio_only=False,
                ))

        has_audio = any(
            f.get("vcodec") == "none" and f.get("acodec") not in ("none", None)
            for f in raw_formats
        )
        if has_audio:
            result.append(Format(
                format_id="bestaudio/best",
                ext="mp3",
                label="Apenas áudio (MP3 192k)",
                is_audio_only=True,
            ))

        return result[:12]

    async def download(
        self, url: str, format_id: str, media_type: str
    ) -> Tuple[str, str, str]:
        if not is_safe_url(url):
            raise ValueError("URL inválida ou não permitida.")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._sync_download, url, format_id, media_type
        )

    def _sync_download(
        self, url: str, format_id: str, media_type: str
    ) -> Tuple[str, str, str]:
        temp_dir = ensure_temp_dir()
        file_id = uuid.uuid4().hex
        output_tpl = str(temp_dir / f"{file_id}.%(ext)s")

        if media_type == "audio":
            opts = {
                **self._base_opts(),
                "format": "bestaudio/best",
                "outtmpl": output_tpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        else:
            opts = {
                **self._base_opts(),
                "format": format_id,
                "outtmpl": output_tpl,
                "merge_output_format": "mp4",
            }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
            except yt_dlp.utils.DownloadError as exc:
                raise ValueError(f"Erro no download: {exc}")

        for f in Path(temp_dir).glob(f"{file_id}.*"):
            size_mb = os.path.getsize(f) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                f.unlink()
                raise ValueError(
                    f"Arquivo ({size_mb:.0f} MB) excede o limite de {MAX_FILE_SIZE_MB} MB."
                )

            ext = f.suffix.lstrip(".")
            mime = "audio/mpeg" if ext == "mp3" else "video/mp4"
            title = (info.get("title") or "download")[:60]
            safe = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            return str(f), f"{safe or 'download'}.{ext}", mime

        raise RuntimeError("Arquivo não encontrado após o download.")