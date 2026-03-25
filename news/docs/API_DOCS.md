# 📚 API ドキュメント

## ベース URL

```
http://localhost:8000  (ローカル)
https://your-api.example.com  (本番)
```

---

## 📄 エンドポイント

### 1. GET `/api/papers` - 全論文取得

**説明:** 全国・全機関の論文データを取得

**パラメータ:**
```
?country=US  # 国コード（オプション）
```

**レスポンス:**
```json
{
  "total_papers": 75,
  "countries": 5,
  "last_updated": "2026-03-25T09:00:00",
  "papers": {
    "US": { "institutions": { ... } },
    "CN": { ... }
  }
}
```

**使用例:**
```bash
# 全論文
curl http://localhost:8000/api/papers

# 日本のみ
curl http://localhost:8000/api/papers?country=JP
```

---

### 2. GET `/api/papers/{country}/{institution}` - 機関別論文取得

**説明:** 特定の国・機関の論文を取得

**パラメータ:**
- `country`: 国コード (US, CN, JP, KR, RU)
- `institution`: 機関キー (MIT, Stanford など)

**レスポンス:**
```json
{
  "country": "US",
  "country_name_ja": "アメリカ",
  "institution": "MIT",
  "institution_name_ja": "マサチューセッツ工科大学",
  "papers_count": 3,
  "papers": [...]
}
```

**使用例:**
```bash
curl http://localhost:8000/api/papers/US/MIT
```

---

### 3. GET `/api/stats` - 統計情報

**説明:** 論文データの統計情報を取得

**レスポンス:**
```json
{
  "total_papers": 75,
  "countries": {
    "US": {
      "total": 15,
      "institutions": {
        "MIT": 3,
        "Stanford": 3,
        ...
      },
      "flag": "🇺🇸",
      "name_ja": "アメリカ"
    },
    ...
  },
  "last_updated": "2026-03-25T09:00:00",
  "timestamp": "2026-03-25T12:34:56"
}
```

**使用例:**
```bash
curl http://localhost:8000/api/stats
```

---

### 4. GET `/api/papers/search` - キーワード検索

**説明:** 論文をキーワードで検索

**パラメータ:**
```
?keyword=AI              # 検索キーワード（必須）
?country=JP             # 国フィルタ（オプション）
?institution=Tokyo      # 機関フィルタ（オプション）
```

**レスポンス:**
```json
{
  "keyword": "AI",
  "results_count": 12,
  "results": [
    {
      "title": "...",
      "summary": "...",
      "country": "US",
      "institution": "MIT",
      ...
    }
  ]
}
```

**使用例:**
```bash
# AI に関する論文
curl http://localhost:8000/api/papers/search?keyword=AI

# 日本の AI 論文
curl http://localhost:8000/api/papers/search?keyword=AI&country=JP
```

---

### 5. POST `/api/analyze-paper` - AI分析

**説明:** 論文をClaude AIで日本語分析

**リクエストボディ:**
```json
{
  "title": "Attention Is All You Need",
  "summary": "This paper introduces the Transformer architecture...",
  "institution": "Google Brain",
  "use_quality_model": false
}
```

**パラメータ:**
- `use_quality_model`:
  - `false` (デフォルト): Claude Haiku（高速、低コスト）
  - `true`: Claude Sonnet（高品質、コスト高）

**レスポンス:**
```json
{
  "analysis": "トランスフォーマーアーキテクチャの登場により...",
  "prospects": "今後のNLP、ビジョンなど幅広い分野への応用が期待できます...",
  "tokens_used": 287,
  "model_used": "claude-haiku-4-5-20251001"
}
```

**使用例:**
```bash
curl -X POST http://localhost:8000/api/analyze-paper \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Attention Is All You Need",
    "summary": "This paper introduces...",
    "use_quality_model": false
  }'
```

---

### 6. POST `/api/run-aggregation` - 論文取得実行

**説明:** 論文取得を即座に開始（バックグラウンド実行）

**レスポンス:**
```json
{
  "status": "started",
  "message": "論文取得を開始しました（バックグラウンド実行）",
  "started_at": "2026-03-25T12:34:56"
}
```

**使用例:**
```bash
curl -X POST http://localhost:8000/api/run-aggregation
```

---

### 7. GET `/health` - ヘルスチェック

**説明:** API の稼働状況確認

**レスポンス:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-25T12:34:56",
  "papers_count": 75,
  "api_version": "1.0.0"
}
```

**使用例:**
```bash
curl http://localhost:8000/health
```

---

### 8. GET `/` - API 情報

**説明:** API のメタ情報表示

**レスポンス:**
```json
{
  "status": "✓ Global Research Terminal API 稼働中",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 🔑 認証

現在、認証は不要です（共有用）

将来的に追加される可能性：
- API キー認証
- JWT トークン認証

---

## ⚡ レート制限

- 通常エンドポイント: 100 requests/minute
- 分析エンドポイント: 30 requests/minute
- 検索エンドポイント: 50 requests/minute

超過時：
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```
ステータス: `429 Too Many Requests`

---

## 🔄 キャッシング

以下のエンドポイントはキャッシュされます（24時間）：

- `/api/papers` (GET)
- `/api/papers/{country}/{institution}` (GET)
- `/api/stats` (GET)
- `/api/analyze-paper` (POST)

キャッシュ確認：
```json
// レスポンスヘッダ
"X-Cache": "HIT"  // キャッシュから返却
"X-Cache": "MISS" // サーバーから取得
```

---

## 📋 レスポンスコード

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 400 | 不正なリクエスト |
| 404 | リソースが見つからない |
| 429 | レート制限超過 |
| 500 | サーバーエラー |

---

## 🧪 テスト方法

### curl でテスト

```bash
# ヘルスチェック
curl http://localhost:8000/health

# 全論文取得
curl http://localhost:8000/api/papers

# 日本の論文
curl http://localhost:8000/api/papers?country=JP

# MIT の論文
curl http://localhost:8000/api/papers/US/MIT
```

### JavaScript でテスト

```javascript
// fetch を使う
async function testAPI() {
  const response = await fetch('http://localhost:8000/api/papers');
  const data = await response.json();
  console.log(data);
}

testAPI();
```

### Python でテスト

```python
import requests

# 全論文取得
response = requests.get('http://localhost:8000/api/papers')
print(response.json())

# AI 分析
response = requests.post(
    'http://localhost:8000/api/analyze-paper',
    json={
        'title': 'Test Paper',
        'summary': 'Test summary'
    }
)
print(response.json())
```

---

## 🌐 CORS

対応：すべてのオリジン

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

本番環境では `ALLOWED_ORIGINS` で制限することを推奨

---

## 📊 レスポンス例

### 成功レスポンス

```json
{
  "total_papers": 75,
  "countries": 5,
  "last_updated": "2026-03-25T09:00:00",
  "papers": { ... }
}
```

### エラーレスポンス

```json
{
  "detail": "Country 'XX' not found"
}
```

---

## 🚀 SDK・クライアント

### JavaScript/TypeScript

```typescript
class GlobalResearchAPI {
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getPapers(country?: string) {
    const url = new URL(`${this.baseUrl}/api/papers`);
    if (country) url.searchParams.set('country', country);
    return fetch(url).then(r => r.json());
  }

  async analyzePaper(title: string, summary: string) {
    return fetch(`${this.baseUrl}/api/analyze-paper`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, summary })
    }).then(r => r.json());
  }
}

// 使用
const api = new GlobalResearchAPI('https://your-api.example.com');
const papers = await api.getPapers('JP');
```

### Python

```python
import requests

class GlobalResearchAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_papers(self, country=None):
        params = {'country': country} if country else {}
        return requests.get(f'{self.base_url}/api/papers', params=params).json()

    def analyze_paper(self, title, summary):
        return requests.post(
            f'{self.base_url}/api/analyze-paper',
            json={'title': title, 'summary': summary}
        ).json()

# 使用
api = GlobalResearchAPI('https://your-api.example.com')
papers = api.get_papers('JP')
```

---

## 📞 サポート

問題が発生した場合：

1. `/health` でサーバーの稼働状況を確認
2. ブラウザの開発者ツール > コンソールでエラーを確認
3. API ドキュメント（`/docs`）で詳細を確認

---

最終更新: 2026年3月25日
