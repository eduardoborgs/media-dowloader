import asyncio
import json
import urllib.request
from typing import Tuple

from models.schemas import Format, MediaInfo
from utils.validators import is_safe_url

class MediaDownloader:

    async def get_info(self, url: str) -> MediaInfo:
        if not is_safe_url(url):
            raise ValueError("URL inválida ou não permitida.")
        
        return MediaInfo(
            title="Mídia pronta para download",
            thumbnail="https://placehold.co/400x200/1e293b/a8a29e?text=M%C3%ADdia+Encontrada", 
            duration=None,
            uploader="Via API Externa (Cobalt)",
            platform="Nuvem",
            formats=[
                Format(format_id="1080", ext="mp4", label="Alta Qualidade (1080p)", is_audio_only=False),
                Format(format_id="720", ext="mp4", label="Qualidade Padrão (720p)", is_audio_only=False),
                Format(format_id="audio", ext="mp3", label="Apenas Áudio (MP3)", is_audio_only=True)
            ]
        )

    async def get_download_redirect(self, url: str, format_id: str, media_type: str) -> str:
        if not is_safe_url(url):
            raise ValueError("URL inválida ou não permitida.")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._sync_get_cobalt_url, url, format_id, media_type
        )

    def _sync_get_cobalt_url(self, url: str, format_id: str, media_type: str) -> str:
        api_endpoints = [
            "https://cobalt-api.pequla.com/api/json",
            "https://cobalt.q-n.space/api/json",
            "https://co.wuk.sh/api/json",
            "https://api.cobalt.tools/api/json" 
        ]
        
        payload = {
            "url": url,
            "filenameStyle": "basic"
        }
        
        if media_type == "audio" or format_id == "audio":
            payload["downloadMode"] = "audio"
            payload["audioFormat"] = "mp3"
        else:
            payload["downloadMode"] = "auto"
            payload["videoQuality"] = format_id if format_id in ["1080", "720"] else "1080"

        data = json.dumps(payload).encode("utf-8")
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for endpoint in api_endpoints:
            req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    status = result.get("status")
                    
                    if status in ["error", "rate-limit"]:
                        continue 
                    
                    download_url = result.get("url")
                    if download_url:
                        return download_url
            except Exception:
                continue
                
        raise ValueError("Todos os servidores externos de processamento estão indisponíveis no momento. Tente novamente.")