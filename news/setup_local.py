#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Setup Script for Global Research Terminal
Sets up automated scheduling for local machine
"""

import platform
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import os

class LocalSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.os_type = platform.system()

    def check_python(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8 or higher required")
            return False
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True

    def check_dependencies(self) -> bool:
        """Check and install required packages"""
        required_packages = ['requests']

        print("\n📦 Checking dependencies...")
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✓ {package} is installed")
            except ImportError:
                print(f"  ⚠ Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        return True

    def create_scheduler_windows(self) -> bool:
        """Create Windows Task Scheduler entry"""
        try:
            print("\n⏰ Setting up Windows Task Scheduler...")

            script_path = self.script_dir / "research_aggregator.py"
            python_exe = sys.executable

            # PowerShell command to create scheduled task
            ps_command = f"""
            $action = New-ScheduledTaskAction -Execute "{python_exe}" -Argument "{script_path}"
            $trigger = New-ScheduledTaskTrigger -Daily -At 09:00
            $principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
            $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

            Register-ScheduledTask -TaskName "GlobalResearchTerminalUpdate" `
                -Action $action `
                -Trigger $trigger `
                -Principal $principal `
                -Settings $settings `
                -Force
            """

            # Execute PowerShell command
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✓ Windows Task Scheduler configured")
                print("  Task: GlobalResearchTerminalUpdate")
                print("  Schedule: Daily at 09:00 AM")
                return True
            else:
                print(f"⚠ Task Scheduler setup needs manual configuration")
                print(f"  Error: {result.stderr}")
                return False

        except Exception as e:
            print(f"⚠ Windows setup failed: {str(e)}")
            return False

    def create_scheduler_macos(self) -> bool:
        """Create macOS LaunchAgent entry"""
        try:
            print("\n⏰ Setting up macOS LaunchAgent...")

            script_path = self.script_dir / "research_aggregator.py"
            python_exe = sys.executable
            home_dir = Path.home()

            # Create LaunchAgent directory if it doesn't exist
            agent_dir = home_dir / "Library" / "LaunchAgents"
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create plist file
            plist_path = agent_dir / "com.globalresearch.terminal.plist"
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.globalresearch.terminal</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{script_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{str(self.script_dir)}/logs/aggregator.log</string>
    <key>StandardErrorPath</key>
    <string>{str(self.script_dir)}/logs/aggregator_error.log</string>
</dict>
</plist>"""

            # Create logs directory
            logs_dir = self.script_dir / "logs"
            logs_dir.mkdir(exist_ok=True)

            with open(plist_path, 'w') as f:
                f.write(plist_content)

            # Load the LaunchAgent
            subprocess.run(["/bin/launchctl", "load", str(plist_path)], check=True)

            print("✓ macOS LaunchAgent configured")
            print(f"  Plist: {plist_path}")
            print("  Schedule: Daily at 09:00 AM")
            return True

        except Exception as e:
            print(f"⚠ macOS setup failed: {str(e)}")
            return False

    def create_scheduler_linux(self) -> bool:
        """Create cron job for Linux"""
        try:
            print("\n⏰ Setting up Linux cron job...")

            script_path = self.script_dir / "research_aggregator.py"
            python_exe = sys.executable
            home_dir = Path.home()

            # Create cron script
            cron_script = self.script_dir / "run_aggregator.sh"
            cron_content = f"""#!/bin/bash
cd {self.script_dir}
{python_exe} research_aggregator.py >> {self.script_dir}/logs/aggregator.log 2>&1
"""

            with open(cron_script, 'w') as f:
                f.write(cron_content)

            # Make executable
            os.chmod(cron_script, 0o755)

            # Create logs directory
            logs_dir = self.script_dir / "logs"
            logs_dir.mkdir(exist_ok=True)

            print("✓ Linux cron script created")
            print(f"\nTo set up automatic execution, add this to your crontab:")
            print(f"  crontab -e")
            print(f"  # Add this line:")
            print(f"  0 9 * * * {cron_script}")
            return True

        except Exception as e:
            print(f"⚠ Linux setup failed: {str(e)}")
            return False

    def create_manual_runner(self) -> bool:
        """Create manual run script"""
        try:
            print("\n🔧 Creating manual run scripts...")

            # Windows batch file
            if self.os_type == "Windows" or True:
                batch_file = self.script_dir / "run_aggregator.bat"
                batch_content = f"""@echo off
cd /d {self.script_dir}
python research_aggregator.py
pause
"""
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                print(f"  ✓ Windows: {batch_file}")

            # Unix shell script
            if self.os_type in ["Darwin", "Linux"] or True:
                shell_file = self.script_dir / "run_aggregator.sh"
                shell_content = f"""#!/bin/bash
cd "{self.script_dir}"
python3 research_aggregator.py
read -p "Press enter to exit..."
"""
                with open(shell_file, 'w') as f:
                    f.write(shell_content)
                os.chmod(shell_file, 0o755)
                print(f"  ✓ Unix: {shell_file}")

            return True

        except Exception as e:
            print(f"⚠ Manual runner creation failed: {str(e)}")
            return False

    def create_config(self) -> bool:
        """Create configuration file"""
        try:
            print("\n⚙️  Creating configuration file...")

            config_file = self.script_dir / "config.json"
            config = {
                "scheduled_time": "09:00",
                "update_interval_days": 1,
                "max_papers_per_institution": 3,
                "search_days_back": 7,
                "data_file": "papers_data.json",
                "html_file": "index.html",
                "created_at": datetime.now().isoformat(),
                "os": self.os_type
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            print(f"  ✓ Config file: {config_file}")
            return True

        except Exception as e:
            print(f"⚠ Config creation failed: {str(e)}")
            return False

    def create_readme(self) -> bool:
        """Create README with setup instructions"""
        try:
            print("\n📖 Creating documentation...")

            readme_file = self.script_dir / "SETUP_README.md"
            readme_content = """# Global Research Terminal - ローカルセットアップガイド

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
"""

            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            print(f"  ✓ Documentation: {readme_file}")
            return True

        except Exception as e:
            print(f"⚠ README creation failed: {str(e)}")
            return False

    def run_setup(self) -> bool:
        """Run full setup"""
        print("╔════════════════════════════════════════════════════════╗")
        print("║   Global Research Terminal - Local Setup               ║")
        print("╚════════════════════════════════════════════════════════╝")

        # Check Python
        if not self.check_python():
            return False

        # Install dependencies
        if not self.check_dependencies():
            return False

        # Create config and docs
        if not self.create_config():
            return False

        if not self.create_readme():
            return False

        if not self.create_manual_runner():
            return False

        # Create scheduler based on OS
        print(f"\nDetected OS: {self.os_type}")

        if self.os_type == "Windows":
            self.create_scheduler_windows()
        elif self.os_type == "Darwin":
            self.create_scheduler_macos()
        elif self.os_type == "Linux":
            self.create_scheduler_linux()

        print("\n" + "=" * 60)
        print("✓ セットアップが完了しました！")
        print("=" * 60)
        print("\n📋 次のステップ：")
        print("  1. SETUP_README.md を読んでください")
        print("  2. 手動実行：run_aggregator.bat または run_aggregator.sh")
        print("  3. または自動スケジュール実行を設定")
        print("\n🌐 ブラウザで index.html を開いて確認してください")
        print("=" * 60 + "\n")

        return True

if __name__ == "__main__":
    setup = LocalSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)
