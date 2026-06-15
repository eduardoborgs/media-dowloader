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
        api_endpoint = "https://api.cobalt.tools/api/json"
        
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
            "User-Agent": "MediaGet/1.0"
        }
        
        req = urllib.request.Request(api_endpoint, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                status = result.get("status")
                if status in ["error", "rate-limit"]:
                    raise ValueError(result.get("text", "Erro interno da API externa."))
                
                return result.get("url")
                
        except Exception as e:
            raise ValueError(f"Não foi possível processar a requisição: {str(e)}")  