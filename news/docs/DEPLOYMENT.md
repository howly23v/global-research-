# 🚀 デプロイガイド

## 推奨デプロイ方式：Railway + Vercel

### メリット
- ✅ ワンコマンドデプロイ
- ✅ 自動スケール
- ✅ GitHub 連携
- ✅ 無料で始められる（後払い）
- ✅ 最もシンプル

---

## ステップ1: リポジトリを作成

```bash
# ローカルで初期化
git init
git add .
git commit -m "Initial commit"

# GitHub で新規リポジトリを作成
# https://github.com/new

# リモートを追加
git remote add origin https://github.com/yourname/global-research.git
git branch -M main
git push -u origin main
```

---

## ステップ2: 環境変数を設定

```bash
# .env.example をコピー
cp .env.example .env

# ANTHROPIC_API_KEY を設定
# https://console.anthropic.com から API キーを取得
```

**重要:**
- `.env` は Git にコミットしない
- `.gitignore` に `.env` が含まれていることを確認

---

## ステップ3: Railway へデプロイ

### 3.1 Railway CLI をインストール

```bash
curl -fsSL cli.new | sh
```

### 3.2 Railway にログイン

```bash
railway login
```

ブラウザで認証します

### 3.3 プロジェクトを初期化

```bash
railway init
```

オプション：
- プロジェクト名を入力（例: global-research）

### 3.4 環境変数を設定

```bash
# API キーを設定
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
```

### 3.5 デプロイ実行

```bash
railway up
```

または GitHub 連携（推奨）：

1. Railway ダッシュボード: `https://railway.app`
2. 新しいプロジェクト作成
3. GitHub リポジトリを接続
4. 自動デプロイを有効化

### 3.6 API URL を確認

```bash
railway open
```

デプロイ後の URL を確認（例：`https://global-research-api-prod.railway.app`）

---

## ステップ4: Vercel へフロントエンドをデプロイ

### 4.1 Vercel にログイン

```bash
# または GitHub からサインアップ
# https://vercel.com
```

### 4.2 GitHub リポジトリを接続

1. Vercel ダッシュボード
2. 「Import Project」
3. GitHub リポジトリを選択
4. 自動デプロイ有効化

### 4.3 環境変数を設定

Vercel 管理画面：

```
Environment Variables:
  REACT_APP_API_URL = https://your-railway-api.app
```

### 4.4 デプロイ完了

自動でホストされます（例：`https://global-research.vercel.app`）

---

## ステップ5: URL を友人に共有

```
フロント URL: https://global-research.vercel.app
API ドキュメント: https://your-railway-api.app/docs
```

---

## 🐳 Docker で本番デプロイ（高度）

### 手順1: Docker イメージをビルド

```bash
docker build -t global-research-api:latest backend/
```

### 手順2: コンテナを実行

```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-xxx \
  -e ENVIRONMENT=production \
  global-research-api:latest
```

### 手順3: Docker Compose で複数コンテナ管理

```bash
docker-compose up -d
```

---

## 🌐 Google Cloud Run へのデプロイ

### 前提条件
- Google Cloud アカウント
- gcloud CLI インストール

### 手順

```bash
# プロジェクルを設定
gcloud config set project YOUR_PROJECT_ID

# Docker イメージをビルド＆プッシュ
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/global-research-api

# Cloud Run にデプロイ
gcloud run deploy global-research-api \
  --image gcr.io/YOUR_PROJECT_ID/global-research-api \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-xxx
```

---

## ⚙️ トラブルシューティング

### エラー: API キーが無効

```bash
# キーを確認
echo $ANTHROPIC_API_KEY

# Railway で設定
railway variables set ANTHROPIC_API_KEY=sk-ant-new-key
```

### エラー: ポートが開いていない

```bash
# Railway でポートを確認
railway logs

# 環境変数 PORT を確認
railway variables list
```

### エラー: データベース接続できない

```bash
# JSON ファイルのパスを確認
railway logs | grep data

# ボリュームマウントを確認（Docker）
docker volume ls
```

### デプロイが遅い

```bash
# ビルドログを確認
railway logs --service=backend

# イメージサイズを削減
docker image ls | grep global-research
```

---

## 🔒 セキュリティチェックリスト

- [ ] `.env` を `.gitignore に追加
- [ ] API キーを環境変数で設定（ハードコードしない）
- [ ] CORS で許可オリジンを制限
- [ ] HTTPS を有効化（Railway/Vercel は自動）
- [ ] レート制限を設定
- [ ] ログを定期的に確認
- [ ] 定期バックアップを実施

---

## 📊 本番環境チェックリスト

- [ ] API サーバーが起動している
- [ ] フロントエンドが API に接続している
- [ ] データが正常に表示されている
- [ ] 自動更新が実行されている
- [ ] エラーログに異常がない
- [ ] レスポンスが 2秒以内

---

## 🔄 継続的デプロイ（CI/CD）

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npx railway up
```

---

## 💰 コスト最適化

| サービス | コスト | 最適化 |
|---------|--------|--------|
| Railway | $5/月 | 使用量に応じて自動スケール |
| Vercel | 無料 | API 呼び出し回数を最小化 |
| Claude API | $2-10/月 | Haiku を使用、キャッシング活用 |
| 合計 | **$7-15/月** | 無料ティアから開始 |

---

## 🚨 監視・アラート

### Railway でアラートを設定

```
1. Railway ダッシュボード
2. Project > Environment
3. Alerts タブ
4. CPU/メモリ使用率でアラート設定
```

### ログを確認

```bash
# Railway ログ
railway logs --service=backend

# エラーのみ
railway logs --service=backend | grep ERROR
```

---

## 🔄 ロールバック（前バージョンに戻す）

### GitHub からロールバック

```bash
git revert HEAD
git push origin main
# 自動でデプロイ（CI/CD）
```

### Railway でロールバック

1. Railway ダッシュボード
2. Deployments タブ
3. 前のバージョンを選択
4. 「Revert」をクリック

---

## 📈 スケーリング

### Railway 自動スケーリング

```
1. Project Settings
2. Deploy
3. Auto-deploy を有効化
4. スケール設定を調整
```

### 手動スケーリング

```bash
# インスタンス数を増やす
railway scale web=2
```

---

## 🔐 バックアップ

### データベースバックアップ

```bash
# JSON データをダウンロード
railway run cat /app/data/papers_data.json > papers_backup.json

# S3 にアップロード（AWS CLI）
aws s3 cp papers_backup.json s3://your-bucket/
```

---

## 📞 サポート

デプロイで問題がある場合：

1. ログを確認: `railway logs`
2. ステータスを確認: https://status.railway.app
3. ドキュメント: https://docs.railway.app
4. サポート: [Railway Community](https://discord.gg/railway)

---

最終更新: 2026年3月25日
