import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from models.schemas import MediaInfo, MediaRequest
from services.downloader import MediaDownloader
from utils.cleanup import cleanup_old_files

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_old_files()  
    yield
    cleanup_old_files()   


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="MediaGet API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENV", "development") != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
    max_age=3600,
)

downloader = MediaDownloader()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/info", response_model=MediaInfo)
@limiter.limit("10/minute")
async def get_media_info(request: Request, body: MediaRequest):
    try:
        return await downloader.get_info(body.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao processar esta URL.")


@app.get("/api/download")
@limiter.limit("5/minute")
async def download_media(
    request: Request,
    url: str = Query(..., description="URL da mídia"),
    format_id: str = Query(default="bestvideo+bestaudio/best"),
    media_type: str = Query(default="video", pattern="^(video|audio)$"),
):
    try:
        file_path, filename, mime_type = await downloader.download(
            url=url, format_id=format_id, media_type=media_type
        )

        file_size = os.path.getsize(file_path)

        def stream_and_cleanup():
            try:
                with open(file_path, "rb") as fh:
                    while chunk := fh.read(1024 * 1024):  
                        yield chunk
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

        return StreamingResponse(
            stream_and_cleanup(),
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(file_size),
                "X-Content-Type-Options": "nosniff",
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao realizar o download.")