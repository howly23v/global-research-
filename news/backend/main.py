#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Research Terminal - FastAPI Backend
マルチユーザー対応・Claude AI統合版
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import anthropic
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import subprocess
from pathlib import Path
import requests
from dotenv import load_dotenv
import asyncio

# ==================== 初期化 ====================
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI アプリ
app = FastAPI(
    title="Global Research Terminal API",
    description="世界の最新研究論文を自動集約するマルチユーザーAPI",
    version="1.0.0"
)

# レート制限
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS設定（友人のブラウザからアクセス可能）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Anthropic クライアント
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ==================== 設定 ====================
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

PAPERS_FILE = DATA_DIR / "papers_data.json"
CACHE_FILE = DATA_DIR / "cache.json"

DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # 低コスト用
QUALITY_MODEL = "claude-sonnet-4-6"  # 高品質用

# ==================== モデル定義 ====================
class PaperAnalysisRequest(BaseModel):
    title: str
    summary: str
    institution: Optional[str] = None
    use_quality_model: bool = False

class PaperAnalysisResponse(BaseModel):
    analysis: str
    prospects: str
    tokens_used: int
    model_used: str

class AggregationResponse(BaseModel):
    status: str
    message: str
    started_at: datetime

class PapersResponse(BaseModel):
    total_papers: int
    countries: int
    last_updated: str
    papers: Dict[str, Any]

# ==================== ユーティリティ関数 ====================

def load_papers_data() -> Dict[str, Any]:
    """論文データを読み込む"""
    if PAPERS_FILE.exists():
        with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"countries": {}, "last_updated": None}

def save_papers_data(data: Dict[str, Any]):
    """論文データを保存"""
    with open(PAPERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_cache(key: str) -> Optional[Dict]:
    """キャッシュを取得"""
    if not CACHE_FILE.exists():
        return None

    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    entry = cache.get(key, {})
    if entry.get("expires_at"):
        expires = datetime.fromisoformat(entry["expires_at"])
        if datetime.now() > expires:
            return None

    return entry.get("data")

def set_cache(key: str, data: Any, ttl_hours: int = 24):
    """キャッシュを設定"""
    cache = {}
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)

    cache[key] = {
        "data": data,
        "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
        "created_at": datetime.now().isoformat()
    }

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ==================== API エンドポイント ====================

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "status": "✓ Global Research Terminal API 稼働中",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    try:
        papers = load_papers_data()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "papers_count": sum(
                len(inst.get("papers", []))
                for country in papers.get("countries", {}).values()
                for inst in country.get("institutions", {}).values()
            ),
            "api_version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/papers", response_model=PapersResponse)
@limiter.limit("100/minute")
async def get_papers(country: Optional[str] = None):
    """
    論文データを取得

    Parameters:
    - country: フィルター対象の国コード（US, CN, JP, KR, RU）
    """
    try:
        papers = load_papers_data()

        if country:
            if country not in papers.get("countries", {}):
                raise HTTPException(status_code=404, detail=f"Country '{country}' not found")
            filtered = {"countries": {country: papers["countries"][country]}}
        else:
            filtered = papers

        total = sum(
            len(inst.get("papers", []))
            for c in filtered.get("countries", {}).values()
            for inst in c.get("institutions", {}).values()
        )

        return PapersResponse(
            total_papers=total,
            countries=len(filtered.get("countries", {})),
            last_updated=papers.get("last_updated", "Unknown"),
            papers=filtered
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching papers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-paper", response_model=PaperAnalysisResponse)
@limiter.limit("30/minute")
async def analyze_paper(request: PaperAnalysisRequest):
    """
    論文をAI分析（Haiku/Sonnetで日本語解析）

    - use_quality_model=True の場合は Sonnet（高品質、コスト高）
    - False の場合は Haiku（高速、低コスト）
    """
    try:
        model = QUALITY_MODEL if request.use_quality_model else DEFAULT_MODEL

        # キャッシュ確認
        cache_key = f"analysis_{hash(request.title + request.summary)}"
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache hit for paper: {request.title[:50]}")
            return PaperAnalysisResponse(
                analysis=cached["analysis"],
                prospects=cached["prospects"],
                tokens_used=0,  # キャッシュなので0
                model_used=f"{model} (cached)"
            )

        # AI分析を実行
        logger.info(f"Analyzing paper with {model}: {request.title[:50]}")

        message = anthropic_client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""
論文「{request.title}」について、日本語で簡潔に分析してください。

要約: {request.summary}

以下の形式で回答（各100字以内）：

【分析】（この研究の重要性と学術的価値）

【発展性】（今後の応用可能性と発展方向）
"""
            }]
        )

        result_text = message.content[0].text

        # レスポンスをパース
        lines = result_text.split("\n")
        analysis = ""
        prospects = ""
        current_section = None

        for line in lines:
            if "分析" in line:
                current_section = "analysis"
            elif "発展性" in line:
                current_section = "prospects"
            elif current_section == "analysis":
                analysis += line + "\n"
            elif current_section == "prospects":
                prospects += line + "\n"

        analysis = analysis.strip()
        prospects = prospects.strip()

        # キャッシュに保存
        result = {
            "analysis": analysis,
            "prospects": prospects
        }
        set_cache(cache_key, result, ttl_hours=24)

        logger.info(f"Analysis completed. Tokens used: {message.usage.output_tokens}")

        return PaperAnalysisResponse(
            analysis=analysis,
            prospects=prospects,
            tokens_used=message.usage.output_tokens,
            model_used=model
        )

    except Exception as e:
        logger.error(f"Error analyzing paper: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/papers/search")
@limiter.limit("50/minute")
async def search_papers(
    keyword: str,
    country: Optional[str] = None,
    institution: Optional[str] = None
):
    """
    キーワード検索

    Parameters:
    - keyword: 検索キーワード
    - country: 国コード（オプション）
    - institution: 機関名（オプション）
    """
    try:
        papers = load_papers_data()
        results = []

        for country_code, country_data in papers.get("countries", {}).items():
            if country and country_code != country:
                continue

            for inst_key, inst_data in country_data.get("institutions", {}).items():
                if institution and institution.lower() not in inst_key.lower():
                    continue

                for paper in inst_data.get("papers", []):
                    if keyword.lower() in paper.get("title", "").lower() or \
                       keyword.lower() in paper.get("summary", "").lower():
                        results.append({
                            **paper,
                            "country": country_code,
                            "institution": inst_key
                        })

        return {
            "keyword": keyword,
            "results_count": len(results),
            "results": results[:50]  # 最大50件
        }

    except Exception as e:
        logger.error(f"Error searching papers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run-aggregation")
@limiter.limit("10/minute")
async def run_aggregation(background_tasks: BackgroundTasks):
    """
    論文取得を即座に実行（バックグラウンド）
    """
    try:
        logger.info("Starting paper aggregation in background")

        # バックグラウンドで実行
        background_tasks.add_task(run_aggregator_task)

        return AggregationResponse(
            status="started",
            message="論文取得を開始しました（バックグラウンド実行）",
            started_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error starting aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_aggregator_task():
    """論文取得タスク（バックグラウンド）"""
    try:
        logger.info("Aggregation task started")

        # research_aggregator.py を実行
        result = subprocess.run(
            ["python", "research_aggregator.py"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            logger.info("Aggregation completed successfully")
        else:
            logger.error(f"Aggregation failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("Aggregation timeout after 300 seconds")
    except Exception as e:
        logger.error(f"Aggregation task failed: {str(e)}")

@app.get("/api/stats")
@limiter.limit("100/minute")
async def get_stats():
    """統計情報取得"""
    try:
        papers = load_papers_data()

        stats = {
            "total_papers": 0,
            "countries": {},
            "last_updated": papers.get("last_updated"),
            "timestamp": datetime.now().isoformat()
        }

        for country_code, country_data in papers.get("countries", {}).items():
            country_total = 0
            institutions = {}

            for inst_key, inst_data in country_data.get("institutions", {}).items():
                inst_papers = len(inst_data.get("papers", []))
                country_total += inst_papers
                institutions[inst_key] = inst_papers

            stats["countries"][country_code] = {
                "total": country_total,
                "institutions": institutions,
                "flag": country_data.get("flag"),
                "name_ja": country_data.get("name_ja")
            }
            stats["total_papers"] += country_total

        return stats

    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/papers/{country}/{institution}")
@limiter.limit("100/minute")
async def get_institution_papers(country: str, institution: str):
    """特定機関の論文取得"""
    try:
        papers = load_papers_data()

        if country not in papers.get("countries", {}):
            raise HTTPException(status_code=404, detail=f"Country '{country}' not found")

        country_data = papers["countries"][country]

        if institution not in country_data.get("institutions", {}):
            raise HTTPException(status_code=404, detail=f"Institution '{institution}' not found")

        inst_data = country_data["institutions"][institution]

        return {
            "country": country,
            "country_name_ja": country_data.get("name_ja"),
            "institution": institution,
            "institution_name_ja": inst_data.get("name_ja"),
            "papers_count": len(inst_data.get("papers", [])),
            "papers": inst_data.get("papers", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching institution papers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feedback/{paper_id}")
@limiter.limit("50/minute")
async def log_feedback(paper_id: str, rating: int = Query(1, ge=1, le=5)):
    """フィードバック記録（UI改善用）"""
    try:
        feedback_file = DATA_DIR / "feedback.jsonl"

        feedback = {
            "timestamp": datetime.now().isoformat(),
            "paper_id": paper_id,
            "rating": rating,
            "user_ip": get_remote_address
        }

        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback, ensure_ascii=False) + "\n")

        return {"status": "recorded", "message": "フィードバックを記録しました"}

    except Exception as e:
        logger.error(f"Error logging feedback: {str(e)}")
        # フィードバック失敗は無視（ユーザーに影響なし）
        return {"status": "error", "message": str(e)}

# ==================== エラーハンドラ ====================

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    """レート制限エラーハンドラ"""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

# ==================== メイン ====================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
