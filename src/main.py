"""Solana ecosystem dashboard — main entry.

Usage:
    python -m src.main                 # collect + render all outputs
    python -m src.main --collect-only  # just refresh data
    python -m src.main --render-only   # re-render from latest JSON
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.collector import collect            # noqa: E402
from src.render_markdown import render_markdown  # noqa: E402
from src.render_html import render_html      # noqa: E402


def main():
    args = sys.argv[1:]
    collect_only = "--collect-only" in args
    render_only = "--render-only" in args

    if not render_only:
        report, json_path = collect()
        print(f"data: {json_path}")
    else:
        files = sorted((ROOT / "reports").glob("solana_ecosystem_*.json"))
        if not files:
            print("no json report; run without --render-only first")
            return 1
        report = json.loads(files[-1].read_text(encoding="utf-8"))
        print(f"data: {files[-1]}")

    date_str = report.get("generated_at", datetime.now(timezone.utc).isoformat())[:10]
    md = render_markdown(report)
    html_doc = render_html(report)

    md_path = ROOT / "reports" / f"solana_ecosystem_{date_str}.md"
    html_path = ROOT / "reports" / "index.html"
    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(html_doc, encoding="utf-8")
    print(f"markdown: {md_path}")
    print(f"html: {html_path}")

    # summary line for stdout (cron-friendly)
    price = report.get("price", {}).get("sol_usdt")
    tvl = report.get("defillama", {}).get("chain_tvl_usd")
    print(f"summary: SOL=${price} TVL=${tvl} anomalies={len(report.get('anomalies', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
