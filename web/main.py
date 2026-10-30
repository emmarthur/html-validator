"""
FastAPI app — HTML structure validator.

Run: python -m uvicorn main:app --reload --port 3033
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

_DEMO_ROOT = Path(__file__).resolve().parent.parent
if str(_DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT))

from html_validator_core import (  # noqa: E402
    analyze_html,
    get_preset_manifest,
    list_preset_manifests,
    load_manifest_yaml,
)

_SAMPLES = _DEMO_ROOT / "data" / "samples"

app = FastAPI(title="HTML Structure Validator")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


class AnalyzeRequest(BaseModel):
    html: str = Field(..., min_length=1)
    manifest_id: str = "report-sections"
    manifest_yaml: str | None = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "help.html")


@app.get("/api/manifests")
async def api_manifests() -> JSONResponse:
    return JSONResponse({"manifests": list_preset_manifests()})


@app.get("/api/samples/{sample_id}")
async def api_sample(sample_id: str) -> JSONResponse:
    path = _SAMPLES / f"{sample_id}.html"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Sample not found")
    return JSONResponse({"id": sample_id, "html": path.read_text(encoding="utf-8")})


@app.post("/api/analyze")
async def api_analyze(body: AnalyzeRequest) -> JSONResponse:
    try:
        if body.manifest_yaml and body.manifest_yaml.strip():
            manifest = load_manifest_yaml(body.manifest_yaml)
        else:
            manifest = get_preset_manifest(body.manifest_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = analyze_html(body.html, manifest)
    payload: dict[str, Any] = result.to_dict()
    return JSONResponse(payload)
