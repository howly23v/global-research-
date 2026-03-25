
import json
import re
from datetime import datetime

# Read the current HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Build SEED_DATA directly
def escape_js_string(s):
    s = str(s)
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    return s

def build_paper_obj(paper):
    """Build a JavaScript paper object"""
    authors_json = json.dumps(paper['authors'], ensure_ascii=False)
    cats_json = json.dumps(paper['categories'], ensure_ascii=False)
    analysis = paper['analysis']
    
    lines = [
        "{",
        f'  title: "{escape_js_string(paper["title"])}",',
        f'  summary: "{escape_js_string(paper["summary"])}",',
        f'  authors: {authors_json},',
        f'  published: "{paper["published"]}",',
        f'  categories: {cats_json},',
        f'  link: "{escape_js_string(paper["link"])}",',
        f'  source: "{escape_js_string(paper["source"])}",',
        f'  institution: "{escape_js_string(paper["institution"])}",',
        f'  institution_ja: "{escape_js_string(paper["institution_ja"])}",',
        f'  country: "{paper["country"]}",',
        f'  analysis: {{analysis: "{escape_js_string(analysis["analysis"])}", prospects: "{escape_js_string(analysis["prospects"])}"}}',
        "}"
    ]
    return "\n                            ".join(lines)

# All papers data
papers_by_country_inst = {
    "US": {
        "MIT": [
            {"title": "Concept Bottleneck Models for Safe AI: Improving Explainability in Safety-Critical Applications", "summary": "AIモデルの予測可能性を向上させるコンセプトボトルネック手法を提案。医療や自動運転などの安全性が重要な分野でAIの説明可能性を大幅に改善し、ユーザーの信頼を構築する新アプローチ。", "authors": [{"name": "J. Yeh et al.", "affiliation": "MIT CSAIL"}], "published": "2026-03-09", "categories": ["cs.AI", "cs.LG"], "link": "https://news.mit.edu/2026/improving-ai-models-ability-explain-predictions-0309", "source": "MIT News", "institution": "MIT", "institution_ja": "マサチューセッツ工科大学", "country": "US", "analysis": {"analysis": "AIの説明可能性問題に対する実践的解決策", "prospects": "医療診断、自動運転、金融判断などの信頼性向上へ貢献"}},
            {"title": "Neural Blueprint: Biomorphic Control Systems for Embodied Intelligence in Soft Robots", "summary": "生体模倣的な神経制御システムでソフトロボットに人間レベルの知能と適応性を付与する新しいアーキテクチャを開発。リハビリ・介護・医療用ロボットの実用化を加速。", "authors": [{"name": "D. Rus et al.", "affiliation": "MIT CSAIL Robotics"}], "published": "2026-02-19", "categories": ["cs.RO", "cs.LG"], "link": "https://news.mit.edu/2026/neural-blueprint-human-intelligence-in-soft-robots-0219", "source": "MIT News", "institution": "MIT", "institution_ja": "マサチューセッツ工科大学", "country": "US", "analysis": {"analysis": "ソフトロボティクスにおける制御の革新的ブレークスルー", "prospects": "福祉・医療ロボットの実現と実用化が加速へ"}},
            {"title": "EnCompass: Automatic Backtracking Framework for LLM-based AI Agents", "summary": "LLMベースのAIエージェント開発を自動化する革新的フレームワーク。プログラマーが手動でバックトラッキングコードを書く必要がなく、開発効率を80%削減。", "authors": [{"name": "M. Yildirim et al.", "affiliation": "MIT CSAIL & Asari AI"}], "published": "2026-02-05", "categories": ["cs.AI", "cs.SE"], "link": "https://news.mit.edu/2026/helping-ai-agents-search-to-get-best-results-from-llms-0205", "source": "MIT News", "institution": "MIT", "institution_ja": "マサチューセッツ工科大学", "country": "US", "analysis": {"analysis": "AI開発プロセスの大幅な効率化を実現", "prospects": "エンタープライズAIの開発スピード大幅向上へ"}}
        ]
    }
}

print("Partial script created - need full data insertion")
