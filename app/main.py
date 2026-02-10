import os
import re
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from .models import ExtractRequest, ExtractResponse, ErrorResponse
from .extractor import VideoExtractor

app = FastAPI(title="Reel to Recipe", version="1.0.0")

API_KEY = os.getenv("API_KEY", "demo-api-key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.post("/extract", response_model=ExtractResponse)
async def extract_recipe(
    request: ExtractRequest,
    authorization: str = Header(None)
):
    # Validate API key
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.replace("Bearer ", "").strip()
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Validate OpenAI key
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    # Validate URL
    url_str = str(request.url)
    supported = ["instagram.com", "tiktok.com", "youtube.com", "youtu.be", 
                 "twitter.com", "x.com", "facebook.com", "fb.watch"]
    if not any(domain in url_str.lower() for domain in supported):
        raise HTTPException(status_code=400, detail="Unsupported URL. Use Instagram, TikTok, YouTube, or Twitter.")
    
    # Extract recipe
    try:
        extractor = VideoExtractor(OPENAI_API_KEY)
        result = extractor.extract(url_str)
        return ExtractResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )
