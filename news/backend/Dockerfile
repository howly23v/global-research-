# マルチステージビルド
FROM python:3.11-slim as builder

WORKDIR /app

# システムパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージをインストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==================== 実行イメージ ====================
FROM python:3.11-slim

WORKDIR /app

# ビルダーステージからpython packagesをコピー
COPY --from=builder /root/.local /root/.local

# 環境変数設定
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# アプリケーションファイルをコピー
COPY main.py .
COPY ../research_aggregator.py .
COPY ../papers_data.json . 2>/dev/null || true

# データディレクトリ作成
RUN mkdir -p /app/data

# 非rootユーザーで実行
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
