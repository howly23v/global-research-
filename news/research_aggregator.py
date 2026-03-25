#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Research Terminal - Automated Research Paper Aggregator
Persona 5 Themed News Terminal for Top Global Research Institutions
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
import sys
from pathlib import Path

# Configuration
INSTITUTIONS = {
    "US": {
        "MIT": "Massachusetts Institute of Technology",
        "Stanford": "Stanford University",
        "Harvard": "Harvard University",
        "Caltech": "California Institute of Technology",
        "UC Berkeley": "University of California Berkeley"
    },
    "CN": {
        "Tsinghua": "Tsinghua University",
        "Peking University": "Peking University",
        "CAS": "Chinese Academy of Sciences",
        "Zhejiang University": "Zhejiang University",
        "Fudan University": "Fudan University"
    },
    "JP": {
        "University of Tokyo": "University of Tokyo",
        "Kyoto University": "Kyoto University",
        "RIKEN": "RIKEN",
        "Osaka University": "Osaka University",
        "Tohoku University": "Tohoku University"
    },
    "KR": {
        "KAIST": "Korea Advanced Institute of Science and Technology",
        "Seoul National University": "Seoul National University",
        "POSTECH": "Pohang University of Science and Technology",
        "Yonsei University": "Yonsei University",
        "KIST": "Korea Institute of Science and Technology"
    },
    "RU": {
        "Moscow State University": "Moscow State University",
        "Russian Academy of Sciences": "Russian Academy of Sciences",
        "MIPT": "Moscow Institute of Physics and Technology",
        "HSE University": "Higher School of Economics",
        "ITMO University": "ITMO University"
    }
}

JAPANESE_NAMES = {
    # US
    "MIT": "マサチューセッツ工科大学",
    "Stanford": "スタンフォード大学",
    "Harvard": "ハーバード大学",
    "Caltech": "カリフォルニア工科大学",
    "UC Berkeley": "カリフォルニア大学バークレー校",
    # China
    "Tsinghua": "清華大学",
    "Peking University": "北京大学",
    "CAS": "中国科学院",
    "Zhejiang University": "浙江大学",
    "Fudan University": "復旦大学",
    # Japan
    "University of Tokyo": "東京大学",
    "Kyoto University": "京都大学",
    "RIKEN": "理化学研究所",
    "Osaka University": "大阪大学",
    "Tohoku University": "東北大学",
    # Korea
    "KAIST": "韓国科学技術院",
    "Seoul National University": "ソウル大学校",
    "POSTECH": "浦項工科大学校",
    "Yonsei University": "延世大学校",
    "KIST": "韓国科学技術研究院",
    # Russia
    "Moscow State University": "モスクワ国立大学",
    "Russian Academy of Sciences": "ロシア科学アカデミー",
    "MIPT": "モスクワ物理工科大学",
    "HSE University": "ロシア高等経済学院",
    "ITMO University": "ITMO大学"
}

class ResearchAggregator:
    def __init__(self, data_file: str = "papers_data.json"):
        self.data_file = Path(data_file)
        self.papers_data = self.load_data()

    def load_data(self) -> Dict[str, Any]:
        """Load existing papers data"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_empty_data()

    def get_empty_data(self) -> Dict[str, Any]:
        """Create empty data structure"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "countries": {}
        }

        for country_code, institutions in INSTITUTIONS.items():
            data["countries"][country_code] = {
                "flag": self.get_flag(country_code),
                "name_ja": self.get_country_ja(country_code),
                "institutions": {}
            }

            for inst_key, inst_name in institutions.items():
                data["countries"][country_code]["institutions"][inst_key] = {
                    "name_ja": JAPANESE_NAMES.get(inst_key, inst_key),
                    "papers": []
                }

        return data

    @staticmethod
    def get_flag(country_code: str) -> str:
        """Get flag emoji for country"""
        flags = {
            "US": "🇺🇸",
            "CN": "🇨🇳",
            "JP": "🇯🇵",
            "KR": "🇰🇷",
            "RU": "🇷🇺"
        }
        return flags.get(country_code, "🌍")

    @staticmethod
    def get_country_ja(country_code: str) -> str:
        """Get country name in Japanese"""
        names = {
            "US": "アメリカ",
            "CN": "中国",
            "JP": "日本",
            "KR": "韓国",
            "RU": "ロシア"
        }
        return names.get(country_code, "その他")

    def fetch_arxiv_papers(self, institution: str, country_code: str) -> List[Dict[str, Any]]:
        """Fetch papers from arXiv API"""
        try:
            # Search arXiv for recent papers from institution
            search_query = f"au:\"{institution}\" AND submittedDate:[{self.get_date_range()}]"
            url = f"http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"

            # Add timeout to prevent hanging
            response = requests.get(url, timeout=10)
            papers = []

            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)

                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    paper = self.parse_arxiv_entry(entry, institution, country_code)
                    if paper:
                        papers.append(paper)

            return papers[:3]  # Limit to 3 papers per institution

        except Exception as e:
            print(f"Error fetching papers for {institution}: {str(e)}")
            return []

    @staticmethod
    def get_date_range() -> str:
        """Get date range for last 7 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        return f"{start_date.strftime('%Y%m%d%H%M%S')} TO {end_date.strftime('%Y%m%d%H%M%S')}"

    @staticmethod
    def parse_arxiv_entry(entry, institution: str, country_code: str) -> Dict[str, Any]:
        """Parse arXiv entry to paper object"""
        try:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}

            title = entry.find('atom:title', ns)
            title_text = title.text.replace('\n', ' ').strip() if title is not None else "Unknown"

            summary = entry.find('atom:summary', ns)
            summary_text = summary.text.replace('\n', ' ').strip() if summary is not None else ""

            published = entry.find('atom:published', ns)
            pub_date = published.text.split('T')[0] if published is not None else datetime.now().strftime('%Y-%m-%d')

            arxiv_id = entry.find('atom:id', ns)
            link = f"https://arxiv.org/abs/{arxiv_id.text.split('/abs/')[-1]}" if arxiv_id is not None else ""

            authors = []
            for author in entry.findall('atom:author', ns):
                author_name = author.find('atom:name', ns)
                if author_name is not None:
                    authors.append({
                        "name": author_name.text,
                        "affiliation": institution
                    })

            return {
                "title": title_text,
                "summary": summary_text[:200] if summary_text else "No summary available",
                "authors": authors[:3],  # Limit to 3 authors
                "published": pub_date,
                "categories": ["cs.AI", "cs.LG"],  # Default categories
                "link": link,
                "source": "arXiv",
                "institution": list(INSTITUTIONS[country_code].keys())[0],
                "institution_ja": JAPANESE_NAMES.get(institution, institution),
                "country": country_code,
                "analysis": {
                    "analysis": "最新の学術研究により、当該分野における革新的な進展が示されています。",
                    "prospects": "本研究は今後の技術発展や応用研究に大きな影響を与える可能性があります。"
                }
            }
        except Exception as e:
            print(f"Error parsing entry: {str(e)}")
            return None

    def generate_japanese_analysis(self, paper: Dict[str, Any]) -> Dict[str, str]:
        """Generate Japanese analysis and prospects"""
        # Template-based generation (can be enhanced with LLM)
        title = paper.get("title", "")
        summary = paper.get("summary", "")

        # Simple keyword-based analysis
        keywords = ["AI", "機械学習", "量子", "バイオ", "エネルギー", "材料"]

        analysis = f"本論文『{title[:50]}...』は、最先端の研究成果を示しています。"
        prospects = "今後の研究開発や実用化に向けて、重要な基盤となる可能性が高いです。"

        return {
            "analysis": analysis,
            "prospects": prospects
        }

    def update_papers(self) -> bool:
        """Update all papers in data"""
        try:
            for country_code, country_data in self.papers_data["countries"].items():
                for inst_key, inst_data in country_data["institutions"].items():
                    print(f"Fetching papers for {inst_key} ({country_code})...")

                    # Fetch papers
                    papers = self.fetch_arxiv_papers(inst_key, country_code)

                    # Add analysis
                    for paper in papers:
                        paper["analysis"] = self.generate_japanese_analysis(paper)

                    # Update data
                    inst_data["papers"] = papers

            # Update timestamp
            self.papers_data["last_updated"] = datetime.now().isoformat()

            return True
        except Exception as e:
            print(f"Error updating papers: {str(e)}")
            return False

    def save_data(self) -> bool:
        """Save papers data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.papers_data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to {self.data_file}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

    def run(self) -> bool:
        """Run the aggregator"""
        print("=" * 60)
        print("Global Research Terminal - Paper Aggregation")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 60)

        # Update papers
        success = self.update_papers()

        if success:
            # Save to file
            self.save_data()
            print("=" * 60)
            print("✓ Aggregation completed successfully")
            print(f"Last updated: {self.papers_data['last_updated']}")
            print("=" * 60)
            return True
        else:
            print("✗ Aggregation failed")
            return False

def main():
    """Main entry point"""
    # Determine data file path
    script_dir = Path(__file__).parent
    data_file = script_dir / "papers_data.json"

    # Create aggregator and run
    aggregator = ResearchAggregator(str(data_file))
    success = aggregator.run()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
