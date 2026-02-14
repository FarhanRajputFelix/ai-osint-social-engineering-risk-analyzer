"""
AI-Based OSINT Correlation and Social Engineering Exposure Analysis System
Main FastAPI Application

CEH-Compliant: Educational and defensive cybersecurity tool.
No private data access, no identity confirmation, no surveillance.
"""

import os
import io
import time
import uuid
import traceback
from typing import Optional
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from engine.image_analyzer import ImageAnalyzer
from engine.username_analyzer import UsernameAnalyzer
from engine.correlation_engine import CorrelationEngine
from engine.risk_assessor import RiskAssessor


# ─── App Configuration ───────────────────────────────────────────────

app = FastAPI(
    title="OSINT Correlation & SE Exposure Analysis",
    description="AI-Based OSINT Correlation and Social Engineering Exposure Analysis System",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage
rate_limit_store = defaultdict(list)
RATE_LIMIT = 30  # Requests per minute
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".jfif", ".png", ".gif", ".webp", ".bmp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp",
    "image/jpg", "image/pjpeg", "image/x-ms-bmp",
}


def validate_image_file(image: UploadFile):
    """Validate an uploaded image by extension AND content type."""
    filename = (image.filename or "").strip()
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    content_type = (image.content_type or "").lower()

    # Accept if EITHER extension or content type is valid
    ext_ok = ext in ALLOWED_EXTENSIONS
    ct_ok = content_type in ALLOWED_CONTENT_TYPES

    if not ext_ok and not ct_ok:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext or content_type}'. "
                   f"Allowed formats: JPG, JPEG, PNG, GIF, WebP, BMP"
        )


# ─── AI Engine Instances ─────────────────────────────────────────────

image_analyzer = ImageAnalyzer()
username_analyzer = UsernameAnalyzer()
correlation_engine = CorrelationEngine()
risk_assessor = RiskAssessor()

# ─── Global Exception Handler ────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch ALL unhandled exceptions and return JSON (never plain text)."""
    traceback.print_exc()  # Log to server console for debugging
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server error: {str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure HTTPExceptions also return proper JSON."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

# ─── Middleware ───────────────────────────────────────────────────────

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    """Simple in-memory rate limiter."""
    if request.url.path.startswith("/api/"):
        client_ip = request.client.host
        now = time.time()
        # Clean old entries
        rate_limit_store[client_ip] = [
            t for t in rate_limit_store[client_ip] if now - t < 60
        ]
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please wait before making more requests."},
            )
        rate_limit_store[client_ip].append(now)

    response = await call_next(request)
    return response


# ─── Static Files ────────────────────────────────────────────────────

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ─── API Routes ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main frontend."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>OSINT Analysis System - Frontend not found</h1>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "system": "AI-Based OSINT Correlation & SE Exposure Analysis",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "engines": {
            "image_analyzer": "ready",
            "username_analyzer": "ready",
            "correlation_engine": "ready",
            "risk_assessor": "ready",
        },
    }


@app.post("/api/analyze/image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze an uploaded image for face detection, perceptual hashing,
    and cross-platform image reuse patterns.
    """
    # Validate file type
    validate_image_file(image)

    # Read and validate size
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")

    if len(contents) == 0:
        raise HTTPException(400, detail="Empty file uploaded")

    # Run analysis
    result = image_analyzer.analyze(contents)

    if result["status"] == "error":
        raise HTTPException(500, detail=result.get("message", "Analysis failed"))

    return {
        "session_id": str(uuid.uuid4()),
        "analysis_type": "image",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **result,
    }


@app.post("/api/analyze/username")
async def analyze_username(
    username: str = Form(...),
    bio: str = Form(""),
    profile_url: str = Form(""),
    location: str = Form(""),
    occupation: str = Form(""),
    education: str = Form(""),
):
    """
    Analyze a username for cross-platform correlation patterns,
    alias detection, and information leakage assessment.
    """
    # Validate input
    username = username.strip()
    if not username:
        raise HTTPException(400, detail="Username cannot be empty")
    if len(username) > 100:
        raise HTTPException(400, detail="Username too long (max 100 characters)")
    if len(bio) > 5000:
        raise HTTPException(400, detail="Bio too long (max 5000 characters)")

    # Run analysis
    result = username_analyzer.analyze(
        username, bio, profile_url, location, occupation, education
    )

    if result["status"] == "error":
        raise HTTPException(500, detail=result.get("message", "Analysis failed"))

    return {
        "session_id": str(uuid.uuid4()),
        "analysis_type": "username",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **result,
    }


@app.post("/api/analyze/full")
async def full_analysis(
    username: str = Form(...),
    bio: str = Form(""),
    profile_url: str = Form(""),
    location: str = Form(""),
    occupation: str = Form(""),
    education: str = Form(""),
    image: UploadFile = File(None),
):
    """
    Full OSINT correlation analysis combining image and username data.
    Produces a comprehensive social engineering exposure risk report.
    """
    # Validate username
    username = username.strip()
    if not username:
        raise HTTPException(400, detail="Username is required for full analysis")
    if len(username) > 100:
        raise HTTPException(400, detail="Username too long (max 100 characters)")

    image_result = None
    username_result = None

    # Image analysis (if provided)
    has_image = False
    try:
        if image is not None and image.filename and image.filename.strip():
            has_image = True
    except Exception:
        has_image = False

    if has_image:
        validate_image_file(image)
        contents = await image.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(400, detail=f"Image too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB")
        if len(contents) > 0:
            image_result = image_analyzer.analyze(contents)

    # Username analysis
    username_result = username_analyzer.analyze(
        username, bio, profile_url, location, occupation, education
    )

    # Correlation
    correlation_result = correlation_engine.correlate(image_result, username_result)

    # Risk assessment
    risk_report = risk_assessor.assess(correlation_result, image_result, username_result)

    return {
        "session_id": str(uuid.uuid4()),
        "analysis_type": "full",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "image_analysis": image_result,
        "username_analysis": username_result,
        "correlation": correlation_result,
        "risk_assessment": risk_report,
    }


# ─── Run Server ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  AI-Based OSINT Correlation & SE Exposure Analysis System")
    print("  CEH-Compliant | Educational Use Only")
    print("=" * 60)
    print("\n  [WEB]  http://localhost:8000")
    print("  [API]  http://localhost:8000/api/health")
    print("  [DOCS] http://localhost:8000/docs")
    print("\n" + "=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
