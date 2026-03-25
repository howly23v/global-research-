#!/usr/bin/env python3
"""
Global Research Paper Aggregator
Fetches latest papers from top institutions in US, China, Japan, Korea, Russia
using arXiv API, Semantic Scholar API, and CrossRef API.
Generates a JSON data file consumed by the frontend.
"""

import requests
import json
import time
import re
import os
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "papers_data.json")

# Top 5 institutions per country with known arXiv affiliations
INSTITUTIONS = {
    "US": {
        "flag": "🇺🇸",
        "name_ja": "アメリカ",
        "institutions": [
            {"name": "MIT", "query": "MIT OR \"Massachusetts Institute of Technology\"", "name_ja": "マサチューセッツ工科大学"},
            {"name": "Stanford", "query": "Stanford University", "name_ja": "スタンフォード大学"},
            {"name": "Harvard", "query": "Harvard University", "name_ja": "ハーバード大学"},
            {"name": "Caltech", "query": "Caltech OR \"California Institute of Technology\"", "name_ja": "カリフォルニア工科大学"},
            {"name": "UC Berkeley", "query": "UC Berkeley OR \"University of California Berkeley\"", "name_ja": "カリフォルニア大学バークレー校"},
        ]
    },
    "CN": {
        "flag": "🇨🇳",
        "name_ja": "中国",
        "institutions": [
            {"name": "Tsinghua", "query": "Tsinghua University", "name_ja": "清華大学"},
            {"name": "Peking University", "query": "Peking University", "name_ja": "北京大学"},
            {"name": "CAS", "query": "Chinese Academy of Sciences", "name_ja": "中国科学院"},
            {"name": "Zhejiang University", "query": "Zhejiang University", "name_ja": "浙江大学"},
            {"name": "Fudan University", "query": "Fudan University", "name_ja": "復旦大学"},
        ]
    },
    "JP": {
        "flag": "🇯🇵",
        "name_ja": "日本",
        "institutions": [
            {"name": "University of Tokyo", "query": "University of Tokyo OR \"東京大学\"", "name_ja": "東京大学"},
            {"name": "Kyoto University", "query": "Kyoto University", "name_ja": "京都大学"},
            {"name": "RIKEN", "query": "RIKEN", "name_ja": "理化学研究所"},
            {"name": "Osaka University", "query": "Osaka University", "name_ja": "大阪大学"},
            {"name": "Tohoku University", "query": "Tohoku University", "name_ja": "東北大学"},
        ]
    },
    "KR": {
        "flag": "🇰🇷",
        "name_ja": "韓国",
        "institutions": [
            {"name": "KAIST", "query": "KAIST", "name_ja": "韓国科学技術院"},
            {"name": "Seoul National University", "query": "Seoul National University", "name_ja": "ソウル大学校"},
            {"name": "POSTECH", "query": "POSTECH OR \"Pohang University\"", "name_ja": "浦項工科大学校"},
            {"name": "Yonsei University", "query": "Yonsei University", "name_ja": "延世大学校"},
            {"name": "KIST", "query": "KIST OR \"Korea Institute of Science and Technology\"", "name_ja": "韓国科学技術研究院"},
        ]
    },
    "RU": {
        "flag": "🇷🇺",
        "name_ja": "ロシア",
        "institutions": [
            {"name": "MSU", "query": "Moscow State University OR Lomonosov", "name_ja": "モスクワ大学"},
            {"name": "RAS", "query": "Russian Academy of Sciences", "name_ja": "ロシア科学アカデミー"},
            {"name": "MIPT", "query": "MIPT OR \"Moscow Institute of Physics\"", "name_ja": "モスクワ物理工科大学"},
            {"name": "HSE", "query": "Higher School of Economics Moscow", "name_ja": "高等経済学院"},
            {"name": "ITMO", "query": "ITMO University", "name_ja": "ITMO大学"},
        ]
    }
}

# Research categories
CATEGORIES = [
    {"id": "cs.AI", "name": "AI・機械学習", "icon": "🤖"},
    {"id": "cs.CL", "name": "自然言語処理", "icon": "💬"},
    {"id": "cs.CV", "name": "コンピュータビジョン", "icon": "👁️"},
    {"id": "physics", "name": "物理学", "icon": "⚛️"},
    {"id": "q-bio", "name": "生命科学", "icon": "🧬"},
    {"id": "cond-mat", "name": "物性物理", "icon": "🔬"},
    {"id": "math", "name": "数学", "icon": "📐"},
    {"id": "eess", "name": "電気工学", "icon": "⚡"},
    {"id": "cs.RO", "name": "ロボティクス", "icon": "🦾"},
    {"id": "quant-ph", "name": "量子物理", "icon": "🔮"},
]


def fetch_arxiv_papers(query, category="", max_results=5):
    """Fetch papers from arXiv API"""
    base_url = "http://export.arxiv.org/api/query"

    search_query = f"all:{query}"
    if category:
        search_query = f"cat:{category} AND all:{query}"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            published = entry.find("atom:published", ns).text

            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.find("atom:name", ns).text
                affiliation = author.find("arxiv:affiliation", ns)
                aff_text = affiliation.text if affiliation is not None else ""
                authors.append({"name": name, "affiliation": aff_text})

            categories = []
            for cat in entry.findall("atom:category", ns):
                categories.append(cat.get("term", ""))

            link = ""
            for l in entry.findall("atom:link", ns):
                if l.get("type") == "text/html":
                    link = l.get("href", "")
                    break
            if not link:
                id_elem = entry.find("atom:id", ns)
                if id_elem is not None:
                    link = id_elem.text

            papers.append({
                "title": title,
                "summary": summary[:500],
                "authors": authors[:5],
                "published": published,
                "categories": categories,
                "link": link,
                "source": "arXiv"
            })

        return papers
    except Exception as e:
        print(f"  Error fetching arXiv for '{query}': {e}")
        return []


def fetch_semantic_scholar(query, max_results=5):
    """Fetch papers from Semantic Scholar API"""
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,authors,year,url,publicationDate,fieldsOfStudy",
        "sort": "publicationDate:desc"
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        papers = []
        for paper in data.get("data", []):
            if not paper.get("title"):
                continue

            authors = []
            for a in (paper.get("authors") or [])[:5]:
                authors.append({"name": a.get("name", ""), "affiliation": ""})

            papers.append({
                "title": paper["title"],
                "summary": (paper.get("abstract") or "")[:500],
                "authors": authors,
                "published": paper.get("publicationDate") or str(paper.get("year", "")),
                "categories": paper.get("fieldsOfStudy") or [],
                "link": paper.get("url") or "",
                "source": "Semantic Scholar"
            })

        return papers
    except Exception as e:
        print(f"  Error fetching Semantic Scholar for '{query}': {e}")
        return []


def generate_analysis(paper):
    """Generate a brief analysis and future prospects for a paper based on its content"""
    title = paper.get("title", "").lower()
    summary = paper.get("summary", "").lower()
    categories = " ".join(paper.get("categories", [])).lower()

    # Keyword-based analysis generation
    analyses = []
    prospects = []

    if any(w in title + summary for w in ["llm", "language model", "transformer", "gpt", "bert", "attention"]):
        analyses.append("大規模言語モデルの性能向上に関する研究")
        prospects.append("次世代AI基盤技術への応用が期待される")
    elif any(w in title + summary for w in ["diffusion", "generative", "image generation", "text-to-image"]):
        analyses.append("生成AIモデルの品質向上に関する研究")
        prospects.append("クリエイティブ産業への革新的応用が見込まれる")
    elif any(w in title + summary for w in ["quantum", "qubit", "entangle"]):
        analyses.append("量子技術の基礎的進展に関する研究")
        prospects.append("量子コンピューティング実用化への貢献が期待される")
    elif any(w in title + summary for w in ["robot", "autonomous", "navigation", "control"]):
        analyses.append("自律型ロボットシステムの革新的手法")
        prospects.append("産業自動化・物流への実用化が加速する可能性")
    elif any(w in title + summary for w in ["protein", "drug", "genome", "cell", "bio", "medical"]):
        analyses.append("バイオテクノロジー・創薬分野の最新研究")
        prospects.append("新薬開発や個別化医療への応用が期待される")
    elif any(w in title + summary for w in ["neural", "deep learning", "reinforcement", "optimization"]):
        analyses.append("深層学習アルゴリズムの改良に関する研究")
        prospects.append("幅広いAI応用分野での精度向上に寄与する")
    elif any(w in title + summary for w in ["climate", "energy", "solar", "battery", "sustain"]):
        analyses.append("環境・エネルギー技術に関する最先端研究")
        prospects.append("持続可能社会の実現に向けた技術革新への貢献")
    elif any(w in title + summary for w in ["security", "crypto", "privacy", "blockchain"]):
        analyses.append("情報セキュリティ基盤技術の研究")
        prospects.append("サイバーセキュリティ強化への実用的応用")
    elif any(w in categories for w in ["physics", "astro", "hep"]):
        analyses.append("物理学の理論的・実験的研究の進展")
        prospects.append("基礎科学の新たな知見を提供する可能性")
    elif any(w in categories for w in ["math", "stat"]):
        analyses.append("数学的理論の新展開")
        prospects.append("他分野への応用可能性を含む基盤的成果")
    else:
        analyses.append("最先端の学術研究の成果")
        prospects.append("関連分野の発展に貢献する重要な知見")

    return {
        "analysis": analyses[0],
        "prospects": prospects[0]
    }


def fetch_all_papers():
    """Fetch papers from all institutions"""
    all_data = {
        "last_updated": datetime.now().isoformat(),
        "countries": {}
    }

    for country_code, country_data in INSTITUTIONS.items():
        print(f"\n{'='*50}")
        print(f"Fetching papers for {country_data['name_ja']} ({country_code})")
        print(f"{'='*50}")

        country_papers = {
            "flag": country_data["flag"],
            "name_ja": country_data["name_ja"],
            "institutions": {}
        }

        for inst in country_data["institutions"]:
            print(f"\n  📚 {inst['name']} ({inst['name_ja']})")

            # Try arXiv first
            papers = fetch_arxiv_papers(inst["query"], max_results=3)
            time.sleep(1)  # Rate limiting

            # Supplement with Semantic Scholar
            if len(papers) < 3:
                ss_papers = fetch_semantic_scholar(f"{inst['name']} 2024 2025 2026", max_results=3)
                papers.extend(ss_papers)
                time.sleep(1)

            # Deduplicate and limit
            seen_titles = set()
            unique_papers = []
            for p in papers:
                title_key = re.sub(r'\s+', ' ', p["title"].lower().strip())
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    p["institution"] = inst["name"]
                    p["institution_ja"] = inst["name_ja"]
                    p["country"] = country_code
                    p["analysis"] = generate_analysis(p)
                    unique_papers.append(p)

            country_papers["institutions"][inst["name"]] = {
                "name_ja": inst["name_ja"],
                "papers": unique_papers[:5]
            }

            print(f"    Found {len(unique_papers[:5])} papers")

        all_data["countries"][country_code] = country_papers

    return all_data


def main():
    print("🔍 Global Research Paper Aggregator Starting...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    data = fetch_all_papers()

    # Count total papers
    total = sum(
        len(inst_data["papers"])
        for country in data["countries"].values()
        for inst_data in country["institutions"].values()
    )

    print(f"\n✅ Total papers fetched: {total}")

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Data saved to {OUTPUT_FILE}")
    return data


if __name__ == "__main__":
    main()
