import asyncio
import json
import urllib.request
import re
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
            uploader="Servidor em Nuvem",
            platform="MediaGet API",
            formats=[
                Format(format_id="best", ext="mp4", label="Melhor Qualidade de Vídeo", is_audio_only=False),
                Format(format_id="audio", ext="mp3", label="Apenas Áudio (MP3)", is_audio_only=True)
            ]
        )

    async def get_download_redirect(self, url: str, format_id: str, media_type: str) -> str:
        if not is_safe_url(url):
            raise ValueError("URL inválida ou não permitida.")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._sync_route_download, url, media_type
        )

    def _sync_route_download(self, url: str, media_type: str) -> str:
        if "youtube.com" in url or "youtu.be" in url:
            return self._get_piped_url(url, media_type)
        else:
            return self._get_cobalt_v7_url(url, media_type)

    def _get_piped_url(self, url: str, media_type: str) -> str:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        if not match:
            raise ValueError("Link do YouTube inválido.")
        video_id = match.group(1)
        
        # Matriz de Redundância (High Availability) com múltiplos nós do Piped
        piped_nodes = [
            "https://pipedapi.tokhmi.xyz",
            "https://piped-api.garudalinux.org",
            "https://pipedapi.drgns.space",
            "https://api.piped.projectsegfau.lt",
            "https://pipedapi.kavin.rocks"
        ]
        
        for node in piped_nodes:
            api_url = f"{node}/streams/{video_id}"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            
            try:
                with urllib.request.urlopen(req, timeout=7) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    
                    if "error" in data:
                        continue
                        
                    if media_type == "audio":
                        streams = data.get("audioStreams", [])
                        if not streams: continue
                        streams.sort(key=lambda x: x.get("bitrate", 0), reverse=True)
                        return streams[0]["url"]
                    else:
                        streams = [s for s in data.get("videoStreams", []) if not s.get("videoOnly", True)]
                        if not streams:
                            streams = data.get("videoStreams", [])
                        if streams:
                            return streams[0]["url"]
            except Exception:
                # Falhou silenciosamente, tenta imediatamente o próximo servidor da lista
                continue

        raise ValueError("Todos os servidores de redundância do YouTube estão inoperantes no momento. Tente em alguns minutos.")

    def _get_cobalt_v7_url(self, url: str, media_type: str) -> str:
        api_endpoints = [
            "https://api.cobalt.tools/",
            "https://cobalt-api.pequla.com/",
            "https://co.wuk.sh/"
        ]
        
        payload = {"url": url}
        if media_type == "audio":
            payload["downloadMode"] = "audio"

        data = json.dumps(payload).encode("utf-8")
        
        # Cabeçalhos com spoofing completo para enganar as travas do Cobalt
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://cobalt.tools",
            "Referer": "https://cobalt.tools/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        for endpoint in api_endpoints:
            req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    
                    download_url = result.get("url")
                    if download_url:
                        return download_url
            except Exception:
                continue
                
        raise ValueError("Todos os servidores externos rejeitaram a conexão no momento.")