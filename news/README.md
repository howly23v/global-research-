# 🎭 Global Research Terminal - API Integration Edition

**世界5ヶ国の最新学術研究を毎日自動集約するマルチユーザー対応Webアプリケーション**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 特徴

- 🤖 **Claude AI統合** - Haiku/Sonnetで日本語分析を自動生成
- 🌍 **グローバル対応** - 5ヶ国25の主要研究機関
- 📱 **マルチユーザー** - URLを共有するだけで複数人がアクセス可能
- ⚡ **低コスト運用** - Claude Haiku で月$2-5
- 🎨 **Persona 5 UI** - 洗練されたダークテーマ
- 🚀 **スケーラブル** - Docker化＆クラウド対応
- 📊 **リアルタイム更新** - API経由で即座にデータ更新可能

## 📋 システム構成

```
┌────────────────────────────────────────────────────────┐
│              Frontend (Vercel)                         │
│          index-api.html + JavaScript                   │
└────────────┬────────────────────────────────────────────┘
             │ HTTPS REST API
             ▼
┌────────────────────────────────────────────────────────┐
│         Backend API (Railway / Cloud Run)              │
│    FastAPI + Claude AI (Haiku/Sonnet)                  │
└────────────┬────────────────────────────────────────────┘
             │ arXiv API, DB
             ▼
┌────────────────────────────────────────────────────────┐
│      Data Layer (Firebase / Local JSON)                │
│         papers_data.json + Cache                       │
└────────────────────────────────────────────────────────┘
```

## 🚀 クイックスタート

### 1️⃣ ローカルで実行（開発環境）

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/global-research-terminal.git
cd global-research-terminal

# 依存パッケージをインストール
pip install -r backend/requirements.txt

# 環境変数を設定
cp .env.example .env
# .env の ANTHROPIC_API_KEY を設定

# バックエンドを起動
cd backend
python main.py

# ブラウザで開く
open http://localhost:8000
```

### 2️⃣ Docker で実行

```bash
docker build -t global-research-api backend/
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-xxx \
  global-research-api:latest

# ブラウザで http://localhost:8000 を開く
```

### 3️⃣ Railway へワンコマンドデプロイ

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# メニューから "1) Railway" を選択
```

## 📚 API ドキュメント

### エンドポイント一覧

#### 📄 データ取得

| メソッド | エンドポイント | 説明 |
|---------|-------------|------|
| GET | `/api/papers` | 全論文データを取得 |
| GET | `/api/papers?country=US` | 国別論文を取得 |
| GET | `/api/papers/{country}/{institution}` | 機関別論文を取得 |
| GET | `/api/stats` | 統計情報を取得 |
| GET | `/api/papers/search?keyword=AI` | キーワード検索 |

#### 🤖 AI分析

| メソッド | エンドポイント | 説明 |
|---------|-------------|------|
| POST | `/api/analyze-paper` | 論文をAI分析（日本語） |

#### 🔄 データ更新

| メソッド | エンドポイント | 説明 |
|---------|-------------|------|
| POST | `/api/run-aggregation` | 論文取得を即座に実行 |

#### 💬 その他

| メソッド | エンドポイント | 説明 |
|---------|-------------|------|
| GET | `/health` | ヘルスチェック |
| GET | `/` | ルート（API情報） |

### リクエスト/レスポンス例

#### 論文データ取得
```bash
curl http://localhost:8000/api/papers?country=US

# レスポンス
{
  "total_papers": 45,
  "countries": 1,
  "last_updated": "2026-03-25T09:00:00",
  "papers": { ... }
}
```

#### 論文をAI分析
```bash
curl -X POST http://localhost:8000/api/analyze-paper \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Attention Is All You Need",
    "summary": "This paper introduces the Transformer architecture...",
    "use_quality_model": false
  }'

# レスポンス
{
  "analysis": "トランスフォーマーアーキテクチャの登場により...",
  "prospects": "今後のNLP、ビジョンなど幅広い分野への応用が期待できます...",
  "tokens_used": 287,
  "model_used": "claude-haiku-4-5-20251001"
}
```

## 🌍 対応研究機関

### 🇺🇸 アメリカ（5）
- MIT
- Stanford University
- Harvard University
- Caltech
- UC Berkeley

### 🇨🇳 中国（5）
- Tsinghua University
- Peking University
- Chinese Academy of Sciences
- Zhejiang University
- Fudan University

### 🇯🇵 日本（5）
- University of Tokyo
- Kyoto University
- RIKEN
- Osaka University
- Tohoku University

### 🇰🇷 韓国（5）
- KAIST
- Seoul National University
- POSTECH
- Yonsei University
- KIST

### 🇷🇺 ロシア（5）
- Moscow State University
- Russian Academy of Sciences
- MIPT
- HSE University
- ITMO University

## 💰 コスト試算（月間）

| サービス | 用途 | コスト |
|---------|------|--------|
| Claude API (Haiku) | AI分析 | $2-5 |
| Railway | バックエンド | 無料〜$5 |
| Vercel | フロントエンド | 無料 |
| Firebase | DB/キャッシュ | 無料ティア |
| **合計** | | **$2-10/月** |

## 🔧 カスタマイズ

### AI モデルを変更

```python
# backend/main.py
DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # 低コスト
QUALITY_MODEL = "claude-sonnet-4-6"  # 高品質
```

### 対応機関を追加

`research_aggregator.py` の `INSTITUTIONS` と `JAPANESE_NAMES` を編集

### フロント URL を変更

```html
<!-- frontend/index-api.html -->
const API_BASE_URL = 'https://your-api-domain.com';
```

## 📖 デプロイオプション

### 推奨: Railway + Vercel（自動デプロイ）

```bash
./scripts/deploy.sh
# メニューで "1) Railway" を選択
```

**利点:**
- ワンコマンドデプロイ
- GitHub 自動連携
- 無料で始められる
- スケール自動対応

### Google Cloud Run（カスタマイズ向け）

```bash
./scripts/deploy.sh
# メニューで "2) Google Cloud Run" を選択
```

### Heroku（従来型）

```bash
./scripts/deploy.sh
# メニューで "3) Heroku" を選択
```

## 🐛 トラブルシューティング

### API が応答しない

```bash
# ヘルスチェック
curl http://localhost:8000/health

# ログを確認
tail -f logs/api.log
```

### Claude API エラー

```bash
# .env で API キーを確認
grep ANTHROPIC_API_KEY .env

# API キーのテスト
python -c "import anthropic; print('OK')"
```

### フロントが API に接続できない

```javascript
// frontend/index-api.html でブラウザコンソルを確認
// Console > 確認してみる
const API_BASE_URL = 'https://your-api-domain.com';
```

## 📝 ログ

ログは以下に保存されます：

```
# バックエンド
logs/api.log
logs/aggregator.log

# ブラウザ
開発者ツール > Console
```

## 🔐 セキュリティ

- ✅ API キーは .env で環理（Git にはコミットしない）
- ✅ CORS で許可オリジンを制限
- ✅ レート制限（100 requests/minute）
- ✅ Docker で非root 実行
- ✅ HTTPS 推奨

## 📚 追加ドキュメント

- [API ドキュメント](docs/API_DOCS.md)
- [デプロイガイド](docs/DEPLOYMENT.md)
- [友人向けセットアップガイド](docs/SETUP_FOR_FRIENDS.md)
- [開発ガイド](docs/DEVELOPMENT.md)

## 🤝 貢献

改善提案やバグ報告は Issue で！

```bash
git checkout -b feature/your-feature
git commit -am 'Add new feature'
git push origin feature/your-feature
```

## 📞 サポート

質問や問題があれば Issue を立ててください。

## 📄 ライセンス

MIT License - [LICENSE](LICENSE) を参照

## 🙏 謝辞

- [Anthropic Claude](https://www.anthropic.com) - AI分析
- [FastAPI](https://fastapi.tiangolo.com) - Web フレームワーク
- [arXiv](https://arxiv.org) - 論文データ

---

**🌟 このプロジェクトを使って何か素晴らしいものを作ってください！**

最終更新: 2026年3月25日
