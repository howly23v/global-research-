# ⚡ QUICKSTART - 3ステップで開始

## 🚀 3分で完成！

### ステップ1️⃣: 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

### ステップ2️⃣: セットアップウィザードを実行
```bash
python setup_local.py
```
✨ 自動でOS別スケジューラが設定されます

### ステップ3️⃣: 初回実行で確認
```bash
python research_aggregator.py
```

### ✅ 完了！
- ブラウザで `index.html` を開く
- 毎日09:00に自動更新開始

---

## 📂 ファイル構成

```
news/
├── 📄 index.html              ← ブラウザで開く
├── 📊 papers_data.json        ← 自動更新される論文データ
├── 🤖 research_aggregator.py  ← メイン実行スクリプト
├── ⚙️ setup_local.py          ← 初期セットアップ
├── 🔄 html_sync.py            ← HTML同期用
├── 📦 requirements.txt         ← 依存パッケージ
├── 🪟 run_aggregator.bat      ← Windows用実行
├── 🐧 run_aggregator.sh       ← Unix用実行
├── 📖 SETUP_GUIDE.md          ← 詳細マニュアル
├── 📝 QUICKSTART.md           ← このファイル
└── 📊 IMPLEMENTATION_SUMMARY.md ← 実装レポート
```

---

## 🎯 何が自動で起こるか？

```
毎日09:00 → 自動実行開始
    ↓
25の研究機関から最新論文を検索
    ↓
最大75論文を収集
    ↓
日本語で分析・解説
    ↓
papers_data.json に保存
    ↓
index.html に自動同期
    ↓
🌐 ブラウザに表示
```

---

## 💻 手動実行方法

### Windows
```cmd
python research_aggregator.py
```
または
```cmd
run_aggregator.bat
```

### macOS / Linux
```bash
python3 research_aggregator.py
```
または
```bash
./run_aggregator.sh
```

---

## 🔧 よくある設定

### 実行時刻を変更（14:00に）

#### Windows
```
Windowsキー → タスクスケジューラ
→ GlobalResearchTerminalUpdate
→ プロパティ → トリガー → 編集 → 時刻変更
```

#### macOS
```bash
# plist ファイルを編集
nano ~/Library/LaunchAgents/com.globalresearch.terminal.plist
# <integer>9</integer> を <integer>14</integer> に変更
# 再度読み込み
launchctl unload ~/Library/LaunchAgents/com.globalresearch.terminal.plist
launchctl load ~/Library/LaunchAgents/com.globalresearch.terminal.plist
```

#### Linux
```bash
crontab -e
# 0 9 * * * を 0 14 * * * に変更
```

---

## 🔍 ログ確認

### ロケーション
```
Windows: news\logs\aggregator.log
Mac/Linux: news/logs/aggregator.log
```

### 確認方法
```bash
# リアルタイムで確認
tail -f logs/aggregator.log

# 最後の20行を表示
tail -20 logs/aggregator.log
```

---

## ❓ トラブル時の確認

### 論文が取得できない
```bash
# インターネット接続確認
ping arxiv.org

# ログファイル確認
cat logs/aggregator_error.log

# 手動実行で詳細確認
python research_aggregator.py -v
```

### スケジューラが動かない

#### Windows
```cmd
tasklist | find "python"
```

#### macOS
```bash
launchctl list | grep global
```

#### Linux
```bash
crontab -l
```

---

## 📊 データ構造

各論文は以下の情報を含みます：
```json
{
  "title": "論文タイトル",
  "summary": "要約（日本語）",
  "published": "2026-03-24",
  "authors": [{"name": "著者", "affiliation": "機関"}],
  "link": "https://arxiv.org/abs/...",
  "institution": "MIT",
  "analysis": {
    "analysis": "日本語での分析",
    "prospects": "将来の発展性"
  }
}
```

---

## 🌍 対応機関（25）

| 国 | 機関 |
|----|------|
| 🇺🇸 | MIT, Stanford, Harvard, Caltech, UC Berkeley |
| 🇨🇳 | Tsinghua, Peking, CAS, Zhejiang, Fudan |
| 🇯🇵 | Tokyo, Kyoto, RIKEN, Osaka, Tohoku |
| 🇰🇷 | KAIST, SNU, POSTECH, Yonsei, KIST |
| 🇷🇺 | Moscow State, RAS, MIPT, HSE, ITMO |

---

## 🎓 カスタマイズ

### 機関を追加
```python
# research_aggregator.py の INSTITUTIONS 辞書に追加
"Stanford": "Stanford University",
"MyUniv": "My University"  # 新規追加
```

### 論文取得数を変更
```python
# research_aggregator.py の fetch_arxiv_papers() 内
return papers[:5]  # 3から5に変更
```

### 検索期間を変更
```python
# research_aggregator.py の get_date_range() 内
timedelta(days=14)  # 7から14日に変更
```

---

## 📞 詳細情報

詳しくは以下をお読みください：
- 📖 **SETUP_GUIDE.md** - 完全ガイド（全4000行）
- 📊 **IMPLEMENTATION_SUMMARY.md** - 実装レポート

---

## ✅ チェックリスト

- [ ] requirements.txt をインストール
- [ ] setup_local.py を実行
- [ ] research_aggregator.py を手動実行
- [ ] papers_data.json にデータが追加されたか確認
- [ ] index.html をブラウザで開いて確認
- [ ] スケジューラが有効になっているか確認

---

**🎉 セットアップ完了！毎日自動で最新論文が表示されます**

質問や問題があれば、ログファイルを確認してください。

最終更新: 2026年3月25日
