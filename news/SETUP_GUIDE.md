# 🎭 Global Research Terminal - ローカル自立動作ガイド

## 概要
**Global Research Terminal** は、世界の最高峰研究機関（米国・中国・日本・韓国・ロシア）の最新論文を毎日自動で収集し、Persona 5のUIテーマで表示するニュース集約サイトです。

### 特徴
- 🌍 5ヶ国、25の主要研究機関に対応
- 🤖 完全自動化で毎日更新
- 🎨 Persona 5の高度なUIデザイン
- 📊 JSON形式の構造化データ
- 🌐 ローカルで独立動作可能

---

## 🚀 クイックスタート

### 1分でセットアップ

```bash
# 1. セットアップスクリプトを実行
python setup_local.py

# 2. 最初の更新を手動実行
python research_aggregator.py

# 3. ブラウザで開く
# index.html をブラウザで開く
```

---

## 📋 システム要件

| 項目 | 要件 |
|------|------|
| Python | 3.8 以上 |
| OS | Windows / macOS / Linux |
| インターネット | 必須（arXiv API接続用） |
| ディスク | 最小10MB |
| メモリ | 最小512MB |

### 依存パッケージ
- **requests**: HTTP通信（arXiv API用）

---

## 📁 ファイル構造と役割

```
news/
├── index.html                    # メインWebサイト（Persona 5 UI）
├── papers_data.json              # 論文データベース（自動更新）
├── research_aggregator.py        # メイン: 論文自動取得スクリプト
├── html_sync.py                  # HTML同期モジュール
├── setup_local.py                # セットアップウィザード
├── config.json                   # 設定ファイル（自動生成）
├── run_aggregator.bat            # Windows用実行スクリプト
├── run_aggregator.sh             # Unix用実行スクリプト
├── SETUP_README.md               # セットアップ説明書（自動生成）
├── SETUP_GUIDE.md                # このファイル
└── logs/
    ├── aggregator.log            # 実行ログ
    └── aggregator_error.log      # エラーログ
```

---

## 🔧 インストール手順

### ステップ1: 依存パッケージのインストール

```bash
python -m pip install requests
```

### ステップ2: セットアップスクリプトの実行

```bash
python setup_local.py
```

このスクリプトが自動で以下を実行します：
- ✓ Python環境チェック
- ✓ 依存パッケージの確認/インストール
- ✓ OS別の自動スケジューラ設定（Windows Task Scheduler / macOS LaunchAgent / Linux cron）
- ✓ 設定ファイル（config.json）の生成
- ✓ 実行スクリプトの生成
- ✓ ドキュメントの生成

### ステップ3: 初回実行（動作確認）

```bash
# Windows
run_aggregator.bat

# macOS / Linux
./run_aggregator.sh
```

---

## 🎯 実行方法

### 方法1: 手動実行

#### Windows
```bash
# コマンドプロンプト
python research_aggregator.py

# またはダブルクリック
run_aggregator.bat
```

#### macOS / Linux
```bash
python3 research_aggregator.py

# またはシェルスクリプト
./run_aggregator.sh
```

### 方法2: 自動実行（スケジューリング）

#### Windows - Task Scheduler（タスクスケジューラ）

セットアップ完了後、以下が自動設定されます：

| 設定項目 | 値 |
|---------|-----|
| タスク名 | GlobalResearchTerminalUpdate |
| トリガー | 毎日 09:00 AM |
| 実行内容 | python research_aggregator.py |

**手動で確認する場合：**
```
Windowsキー → タスクスケジューラ → GlobalResearchTerminalUpdate
```

#### macOS - LaunchAgent

セットアップ完了後、以下が自動設定されます：

```bash
~/Library/LaunchAgents/com.globalresearch.terminal.plist
```

**状態確認：**
```bash
launchctl list | grep global
```

**手動で無効化する場合：**
```bash
launchctl unload ~/Library/LaunchAgents/com.globalresearch.terminal.plist
```

**再度有効化する場合：**
```bash
launchctl load ~/Library/LaunchAgents/com.globalresearch.terminal.plist
```

#### Linux - Cron

セットアップ後、以下を手動で設定してください：

```bash
# cronジョブを編集
crontab -e

# 以下の行を追加（毎日09:00実行）
0 9 * * * /path/to/news/run_aggregator.sh

# 確認
crontab -l
```

**よく使うcron設定：**
```bash
# 毎日09:00
0 9 * * * /path/to/news/run_aggregator.sh

# 毎日12:00
0 12 * * * /path/to/news/run_aggregator.sh

# 1時間ごと（00分）
0 * * * * /path/to/news/run_aggregator.sh

# 毎週月曜09:00
0 9 * * 1 /path/to/news/run_aggregator.sh

# 1日ごと（00:00）
0 0 * * * /path/to/news/run_aggregator.sh
```

---

## 📊 動作の詳細

### データフロー

```
research_aggregator.py
    ↓
1. arXiv APIから論文データを検索
2. 25機関×最大3論文を取得
3. 日本語での分析・解説を生成
4. papers_data.json に保存
    ↓
html_sync.py
    ↓
5. JSON データを HTML に同期
6. ブラウザで表示
    ↓
index.html (Persona 5 UI)
```

### 検索対象機関（25機関）

| 地域 | 機関 |
|------|------|
| 🇺🇸 アメリカ | MIT、スタンフォード大学、ハーバード大学、カルテック、UC Berkeley |
| 🇨🇳 中国 | 清華大学、北京大学、中国科学院、浙江大学、復旦大学 |
| 🇯🇵 日本 | 東京大学、京都大学、理化学研究所、大阪大学、東北大学 |
| 🇰🇷 韓国 | KAIST、ソウル大学、POSTECH、延世大学、KIST |
| 🇷🇺 ロシア | モスクワ国立大学、ロシア科学アカデミー、MIPT、HSE大学、ITMO大学 |

### 論文データの構造

各論文には以下の情報が含まれます：

```json
{
  "title": "論文のタイトル",
  "summary": "論文の要約（日本語）",
  "authors": [
    {"name": "著者名", "affiliation": "所属機関"}
  ],
  "published": "2026-03-24",
  "categories": ["cs.AI", "cs.LG"],
  "link": "https://arxiv.org/abs/...",
  "source": "arXiv",
  "institution": "MIT",
  "institution_ja": "マサチューセッツ工科大学",
  "country": "US",
  "analysis": {
    "analysis": "日本語での分析・評価",
    "prospects": "日本語での将来の発展性"
  }
}
```

---

## ⚙️ カスタマイズ

### 実行時間の変更

#### Windows (Task Scheduler)
1. タスクスケジューラを開く
2. GlobalResearchTerminalUpdate を右クリック
3. プロパティ → トリガー → 編集
4. 時刻を変更

#### macOS (LaunchAgent)
1. `~/Library/LaunchAgents/com.globalresearch.terminal.plist` を編集
2. `<integer>9</integer>` を希望の時間に変更（24時間形式）
3. `launchctl unload` → `launchctl load` で再読み込み

#### Linux (cron)
```bash
crontab -e
# 例：毎日14:00に実行
0 14 * * * /path/to/news/run_aggregator.sh
```

### 取得論文数の変更

`research_aggregator.py` を編集：

```python
# 機関あたりの論文数（現在: 3）
return papers[:3]  # この数を変更

# 検索期間の日数（現在: 7日）
start_date = end_date - timedelta(days=7)  # この数を変更
```

### 検索対象機関の追加

`research_aggregator.py` の `INSTITUTIONS` と `JAPANESE_NAMES` に追加：

```python
INSTITUTIONS = {
    "US": {
        "MIT": "Massachusetts Institute of Technology",
        "Stanford": "Stanford University",
        # 新規追加
        "Cornell": "Cornell University"
    }
}

JAPANESE_NAMES = {
    "MIT": "マサチューセッツ工科大学",
    "Stanford": "スタンフォード大学",
    # 新規追加
    "Cornell": "コーネル大学"
}
```

---

## 🔍 トラブルシューティング

### Q: 論文が取得できない

**A:** 以下を確認してください

```bash
# 1. インターネット接続の確認
ping arxiv.org

# 2. ファイアウォール設定
# arXiv APIへのアクセスがブロックされていないか確認

# 3. ログの確認
tail -f logs/aggregator.log  # macOS/Linux
type logs\aggregator.log     # Windows

# 4. arXiv APIの状態確認
# https://arxiv.org/status へアクセス
```

### Q: スケジュール実行されない

**A:**

**Windows の場合：**
```cmd
# タスクスケジューラを確認
tasklist | find "python"

# タスクの実行履歴を確認
# タスクスケジューラ → GlobalResearchTerminalUpdate → 履歴
```

**macOS の場合：**
```bash
# LaunchAgentの状態確認
launchctl list | grep global

# 再度有効化
launchctl load ~/Library/LaunchAgents/com.globalresearch.terminal.plist

# ログ確認
tail -f ~/Library/Logs/com.globalresearch.terminal.log
```

**Linux の場合：**
```bash
# crontab の確認
crontab -l

# syslog の確認
grep CRON /var/log/syslog | tail -20

# システムジャーナルの確認
journalctl -u cron
```

### Q: メモリ使用量が多い

**A:** 以下を試してください

```python
# research_aggregator.py で機関あたりの論文数を減らす
return papers[:1]  # 1論文のみ取得

# または実行頻度を減らす
# crontab で実行回数を減らす
```

### Q: 文字エンコードエラー

**A:** Python 3のデフォルト設定を確認：

```bash
python -c "import sys; print(sys.getdefaultencoding())"
# UTF-8 であることを確認
```

### Q: arXiv APIが遅い

**A:** arXivは毎秒1リクエストの制限があります。複数回実行する場合は数秒待機してください。

---

## 📊 ログ管理

### ログ位置
- Windows: `news\logs\aggregator.log`
- macOS: `~/Library/Logs/com.globalresearch.terminal.log`
- Linux: ローカルディレクトリ内の `logs/aggregator.log`

### ログレベル
```
INFO  - 正常実行ログ
WARNING - 警告（データ未取得など）
ERROR - エラー
```

### ログをクリア
```bash
# ファイルをリセット
rm logs/aggregator.log logs/aggregator_error.log

# または
> logs\aggregator.log  # Windows PowerShell
```

---

## 🌐 ブラウザでの確認

### ローカルでの表示方法

1. **index.html をブラウザで開く**
   ```bash
   # Windows
   start index.html

   # macOS
   open index.html

   # Linux
   firefox index.html
   ```

2. **ローカルWebサーバーで実行（推奨）**
   ```bash
   # Python 3
   python -m http.server 8000

   # ブラウザで開く
   # http://localhost:8000
   ```

---

## 🚨 セキュリティ注意事項

- ✓ ローカルのみで実行（外部ホスティング不要）
- ✓ 個人情報は含まれない
- ✓ arXivの利用規約に準拠
- ⚠️ インターネット接続時はアクセスログが記録される

---

## 📈 パフォーマンス最適化

### 実行時間の短縮

```python
# 1. 検索機関数を減らす
# 全25機関 → 各国1機関のみにする

# 2. 論文数を減らす
return papers[:1]  # 1論文に

# 3. 検索期間を短くする
timedelta(days=1)  # 1日のみ検索
```

### メモリ使用量の削減

```python
# バッチ処理を導入
# 1機関ごとにメモリをクリア
```

---

## 🔄 定期メンテナンス

### 週1回実施
```bash
# ログファイルのローテーション
# 古いログをアーカイブ
```

### 月1回実施
```bash
# papers_data.json のバックアップ
cp papers_data.json papers_data.json.backup.$(date +%Y%m%d)
```

---

## 💡 ベストプラクティス

1. **定期的なバックアップ**
   ```bash
   # 重要ファイルのバックアップ
   cp papers_data.json papers_data_backup.json
   ```

2. **ログの定期確認**
   ```bash
   # 週1回ログを確認
   tail logs/aggregator.log
   ```

3. **実行結果の検証**
   - 毎回 index.html をブラウザで確認
   - 論文の数と内容が正しいか確認

4. **設定値の記録**
   - config.json を安全な場所にバックアップ
   - カスタマイズ内容をドキュメント化

---

## 📞 サポート情報

### よくある質問への回答集

**Q: macOS で実行権限エラーが出る**
```bash
chmod +x run_aggregator.sh
./run_aggregator.sh
```

**Q: Windows でPythonが見つからない**
```cmd
# Python をインストール時に PATH に追加したことを確認
python --version
```

**Q: JSON が破損した場合**
```bash
# バックアップから復元
cp papers_data.json.backup papers_data.json
```

---

## 📚 参考リンク

- [arXiv API ドキュメント](https://arxiv.org/help/api)
- [Python requests ライブラリ](https://requests.readthedocs.io/)
- [Windows Task Scheduler](https://docs.microsoft.com/ja-jp/windows/desktop/taskschd/task-scheduler-start-page)
- [macOS LaunchAgent](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchAgents.html)
- [Linux cron](https://linux.die.net/man/5/crontab)

---

## ✅ チェックリスト

- [ ] Python 3.8 以上がインストール済み
- [ ] requests パッケージをインストール
- [ ] setup_local.py を実行
- [ ] 初回手動実行で動作確認
- [ ] papers_data.json に論文が追加されたことを確認
- [ ] index.html をブラウザで確認
- [ ] 自動スケジュール実行を確認
- [ ] ログファイルを定期確認予定

---

**🎉 セットアップ完了後は、毎日自動で最新の研究論文が表示されます！**

最終更新: 2026年3月25日
