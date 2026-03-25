# Global Research Terminal - ローカルセットアップガイド

## 概要
このツールは、米国・中国・日本・韓国・ロシアの大学・研究機関からの最新論文を自動で収集し、
Persona 5のUIテーマで表示するニュースサイトを更新します。

## システム要件
- Python 3.8 以上
- インターネット接続
- OS: Windows / macOS / Linux

## インストール手順

### 1. 依存パッケージのインストール
```bash
python -m pip install requests
```

### 2. セットアップスクリプトの実行
```bash
python setup_local.py
```

## 実行方法

### 手動実行
- **Windows**: `run_aggregator.bat` をダブルクリック
- **macOS/Linux**: `./run_aggregator.sh` を実行

### 自動実行（スケジュール）

#### Windows
セットアップスクリプト実行後、タスクスケジューラが自動設定されます：
- タスク名：GlobalResearchTerminalUpdate
- 実行時刻：毎日 09:00

#### macOS
セットアップスクリプト実行後、LaunchAgentが自動設定されます：
- ファイル：~/Library/LaunchAgents/com.globalresearch.terminal.plist
- 実行時刻：毎日 09:00

#### Linux
手動でcronジョブを設定してください：
```bash
crontab -e
# 以下を追加：
0 9 * * * /path/to/run_aggregator.sh
```

## ファイル構造
```
news/
├── index.html              # メインWebサイト
├── papers_data.json        # 論文データ（自動更新）
├── research_aggregator.py  # メインスクリプト
├── setup_local.py          # セットアップスクリプト
├── config.json             # 設定ファイル
├── run_aggregator.bat      # Windows用実行スクリプト
├── run_aggregator.sh       # Unix用実行スクリプト
└── logs/                   # 実行ログ

```

## トラブルシューティング

### 論文が取得できない場合
- インターネット接続を確認
- arXiv APIのレート制限（毎秒1リクエスト）に確認
- logs/aggregator.log でエラーを確認

### スケジュール実行されない場合
- **Windows**: タスクスケジューラの状態を確認
- **macOS**: `launchctl list | grep global` で状態確認
- **Linux**: `crontab -l` で登録確認

### APIエラー
arXiv APIに接続できない場合、数秒待機して再試行してください。

## カスタマイズ

### 実行時刻の変更
`config.json` の `scheduled_time` を変更：
```json
{
  "scheduled_time": "14:00"
}
```

### 取得期間の変更
`research_aggregator.py` の `get_date_range()` を編集

### 対応機関の追加
`research_aggregator.py` の `INSTITUTIONS` 辞書に追加

## サポート
ログファイルは `logs/` ディレクトリに保存されます。
問題発生時はログを確認してください。
