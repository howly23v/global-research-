#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Sync Module - Synchronizes papers_data.json with index.html
Ensures the website displays the latest research data
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class HTMLSync:
    """Synchronize JSON data with HTML display"""

    def __init__(self, data_file: str = "papers_data.json", html_file: str = "index.html"):
        self.data_file = Path(data_file)
        self.html_file = Path(html_file)

    def load_json_data(self) -> Dict[str, Any]:
        """Load papers data from JSON"""
        if not self.data_file.exists():
            print(f"⚠ Data file not found: {self.data_file}")
            return {}

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {str(e)}")
            return {}

    def load_html(self) -> str:
        """Load HTML file"""
        if not self.html_file.exists():
            print(f"⚠ HTML file not found: {self.html_file}")
            return ""

        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error loading HTML: {str(e)}")
            return ""

    def generate_script_data(self, data: Dict[str, Any]) -> str:
        """Generate JavaScript data object from JSON"""
        try:
            # Convert Python dict to JavaScript
            js_data = f"""
// ================== GLOBAL RESEARCH TERMINAL DATA ==================
// Last updated: {data.get('last_updated', 'N/A')}
// Auto-generated from papers_data.json
// =====================================================================

const SEED_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};

// Update last_updated timestamp on page
document.addEventListener('DOMContentLoaded', () => {{
    const lastUpdated = document.getElementById('last-updated');
    if (lastUpdated && SEED_DATA.last_updated) {{
        const date = new Date(SEED_DATA.last_updated);
        lastUpdated.textContent = date.toLocaleString('ja-JP');
    }}
}});

// =====================================================================
"""
            return js_data
        except Exception as e:
            print(f"❌ Error generating script data: {str(e)}")
            return ""

    def update_html_data(self, html: str, data: Dict[str, Any]) -> str:
        """Update SEED_DATA in HTML"""
        if not html:
            return html

        # Find the script section with SEED_DATA
        pattern = r'(// ================== GLOBAL RESEARCH TERMINAL DATA.*?// =====================================================================\s*\n)'

        new_script = self.generate_script_data(data)

        if re.search(pattern, html, re.DOTALL):
            # Replace existing SEED_DATA block
            html = re.sub(pattern, new_script, html, flags=re.DOTALL)
        else:
            # If no SEED_DATA found, try to insert before closing body tag
            print("⚠ SEED_DATA block not found, attempting to insert...")
            script_tag = f"<script>\n{new_script}\n</script>\n</body>"
            html = re.sub(r'</body>', script_tag, html)

        return html

    def generate_ticker_content(self, data: Dict[str, Any]) -> str:
        """Generate ticker content with latest headlines"""
        headlines = []

        # Extract first papers from each country
        for country_code, country_data in data.get("countries", {}).items():
            for inst_key, inst_data in country_data.get("institutions", {}).items():
                papers = inst_data.get("papers", [])
                if papers:
                    first_paper = papers[0]
                    title = first_paper.get("title", "No title")
                    # Truncate title for ticker
                    ticker_title = title[:60] + "..." if len(title) > 60 else title
                    headlines.append(f"🔴 {ticker_title}")

        # Return first 5 headlines as ticker
        return " | ".join(headlines[:5]) if headlines else "Loading research papers..."

    def sync(self) -> bool:
        """Synchronize JSON data with HTML"""
        print("=" * 60)
        print("🔄 Synchronizing HTML with latest data...")
        print("=" * 60)

        # Load data
        data = self.load_json_data()
        if not data:
            print("❌ No data to sync")
            return False

        # Load HTML
        html = self.load_html()
        if not html:
            print("❌ Could not load HTML")
            return False

        # Update HTML with data
        updated_html = self.update_html_data(html, data)

        # Save updated HTML
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(updated_html)
            print(f"✓ HTML updated successfully")
        except Exception as e:
            print(f"❌ Error saving HTML: {str(e)}")
            return False

        # Show sync summary
        total_papers = 0
        for country_data in data.get("countries", {}).values():
            for inst_data in country_data.get("institutions", {}).values():
                total_papers += len(inst_data.get("papers", []))

        print(f"✓ Total papers synced: {total_papers}")
        print(f"✓ Last updated: {data.get('last_updated', 'N/A')}")
        print("=" * 60)

        return True

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent

    sync = HTMLSync(
        str(script_dir / "papers_data.json"),
        str(script_dir / "index.html")
    )

    success = sync.sync()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
