#!/bin/bash

# ==================== Global Research Terminal - ワンクリックデプロイスクリプト ====================

set -e

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ロゴ表示
clear
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Global Research Terminal - Deploy Script              ║"
echo "║  マルチユーザー対応API統合版                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==================== 関数定義 ====================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 がインストールされていません"
        return 1
    fi
    return 0
}

# ==================== 前提条件チェック ====================

log_info "前提条件をチェック中..."

if ! check_command git; then
    log_error "Git をインストールしてください"
    exit 1
fi

if ! check_command python3; then
    log_error "Python 3 をインストールしてください"
    exit 1
fi

log_success "前提条件OK"

# ==================== デプロイ先選択 ====================

echo ""
echo -e "${YELLOW}デプロイ先を選択してください:${NC}"
echo "1) Railway + Vercel（推奨・自動設定）"
echo "2) Google Cloud Run（手動設定）"
echo "3) Heroku（従来型）"
echo "4) ローカルDocker（テスト用）"
echo ""
read -p "選択 (1-4): " DEPLOY_CHOICE

case $DEPLOY_CHOICE in
    1)
        DEPLOY_TARGET="railway"
        ;;
    2)
        DEPLOY_TARGET="cloudrun"
        ;;
    3)
        DEPLOY_TARGET="heroku"
        ;;
    4)
        DEPLOY_TARGET="docker"
        ;;
    *)
        log_error "無効な選択"
        exit 1
        ;;
esac

log_info "デプロイターゲット: $DEPLOY_TARGET"

# ==================== GitHub リポジトリ初期化 ====================

log_info "GitHub リポジトリ設定中..."

if [ ! -d ".git" ]; then
    read -p "GitHub リポジトリURL (例: https://github.com/user/repo.git): " REPO_URL
    git init
    git add .
    git commit -m "Initial commit: Global Research Terminal API"
    git branch -M main
    git remote add origin $REPO_URL
    git push -u origin main
    log_success "GitHub リポジトリに push しました"
else
    log_warning "既存の Git リポジトリを使用します"
fi

# ==================== 環境変数ファイル作成 ====================

log_info "環境変数ファイルを作成中..."

cat > .env << EOF
# Anthropic API
ANTHROPIC_API_KEY=sk-your-api-key-here

# サーバー設定
PORT=8000
ENVIRONMENT=production

# リモートバックエンド URL（フロント用）
REACT_APP_API_URL=https://your-api-domain.com

# レート制限
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=60
EOF

log_success ".env ファイルを作成しました"
log_warning "ANTHROPIC_API_KEY を設定してください"

# ==================== デプロイ処理 ====================

case $DEPLOY_TARGET in
    railway)
        log_info "Railway へのデプロイを準備中..."

        # Railway CLI チェック
        if ! check_command railway; then
            log_info "Railway CLI をインストール中..."
            curl -fsSL cli.new | sh
        fi

        log_info "Railway にログイン..."
        railway login

        log_info "プロジェクト初期化..."
        railway init

        log_info "環境変数を設定..."
        railway variables set ANTHROPIC_API_KEY
        railway variables set REACT_APP_API_URL

        log_info "デプロイ中..."
        railway deploy

        log_success "Railway へのデプロイが完了しました！"
        railway open
        ;;

    cloudrun)
        log_info "Google Cloud Run へのデプロイを準備中..."

        if ! check_command gcloud; then
            log_error "gcloud CLI をインストールしてください"
            exit 1
        fi

        read -p "GCP プロジェクトID: " GCP_PROJECT_ID
        read -p "リージョン (例: asia-northeast1): " GCP_REGION

        gcloud config set project $GCP_PROJECT_ID

        log_info "Docker イメージをビルド中..."
        gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/global-research-api

        log_info "Cloud Run にデプロイ中..."
        gcloud run deploy global-research-api \
            --image gcr.io/$GCP_PROJECT_ID/global-research-api \
            --platform managed \
            --region $GCP_REGION \
            --allow-unauthenticated \
            --set-env-vars ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f 2)

        log_success "Cloud Run へのデプロイが完了しました！"
        ;;

    heroku)
        log_info "Heroku へのデプロイを準備中..."

        if ! check_command heroku; then
            log_error "Heroku CLI をインストールしてください"
            exit 1
        fi

        heroku login

        read -p "Heroku アプリ名: " HEROKU_APP

        log_info "Heroku アプリを作成中..."
        heroku create $HEROKU_APP || true

        log_info "環境変数を設定中..."
        ANTHROPIC_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f 2)
        heroku config:set ANTHROPIC_API_KEY=$ANTHROPIC_KEY --app=$HEROKU_APP

        log_info "Heroku にデプロイ中..."
        git push heroku main

        log_success "Heroku へのデプロイが完了しました！"
        heroku open --app=$HEROKU_APP
        ;;

    docker)
        log_info "ローカル Docker でテスト実行中..."

        log_info "Docker イメージをビルド中..."
        docker build -t global-research-api:latest backend/

        log_info "コンテナを起動中..."
        docker run -p 8000:8000 \
            -e ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f 2) \
            global-research-api:latest

        log_success "Docker コンテナが起動しました"
        log_info "ブラウザで http://localhost:8000 を開いてください"
        ;;
esac

# ==================== デプロイ後処理 ====================

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  デプロイが完了しました！                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"

echo ""
log_info "次のステップ:"
echo "  1. .env ファイルで ANTHROPIC_API_KEY を設定"
echo "  2. API サーバーが起動していることを確認"
echo "  3. フロント (frontend/index-api.html) をブラウザで開く"
echo "  4. 'API_URL' をリモートサーバーのURLに変更"
echo ""

log_success "セットアップが完了しました！"
