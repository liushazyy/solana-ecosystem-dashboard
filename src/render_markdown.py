"""Markdown report generator for the Solana ecosystem dashboard."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def _fmt_usd(v, nd=0):
    try:
        v = float(v)
        if v >= 1e9:
            return f"${v/1e9:.2f}B"
        if v >= 1e6:
            return f"${v/1e6:.2f}M"
        if v >= 1e3:
            return f"${v/1e3:.2f}K"
        return f"${v:,.{nd}f}"
    except (TypeError, ValueError):
        return "n/a"


def _fmt_sol(v):
    try:
        return f"{float(v):,.0f} SOL"
    except (TypeError, ValueError):
        return "n/a"


def render_markdown(report: dict) -> str:
    dl = report.get("defillama", {})
    price = report.get("price", {})
    sc = report.get("stablecoins", {})
    rpc = report.get("rpc", {})
    anomalies = report.get("anomalies", [])
    ts = report.get("generated_at", "")

    lines = []
    lines.append("# Solana Ecosystem Report")
    lines.append("")
    lines.append(f"*Generated: {ts} UTC | Source: on-chain RPC + DeFiLlama + exchange tickers*")
    lines.append("")

    # Anomaly summary
    if anomalies:
        lines.append("## ⚠️ Anomaly Alerts")
        lines.append("")
        for a in anomalies:
            lines.append(f"- **{a['severity'].upper()}** — {a['metric']}: {a['detail']}")
        lines.append("")

    # 1. Network performance
    lines.append("## 1. Network Performance")
    lines.append("")
    epoch = rpc.get("epoch_info") or {}
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Slot | {rpc.get('slot', 'n/a')} |")
    lines.append(f"| Epoch | {epoch.get('epoch', 'n/a')} |")
    lines.append(f"| Slot index in epoch | {epoch.get('slotIndex', 'n/a')} / {epoch.get('slotsInEpoch', 'n/a')} |")
    lines.append(f"| TPS (recent sample) | {rpc.get('tps', 'n/a'):.0f} |" if rpc.get("tps") else f"| TPS | n/a |")
    lines.append(f"| Block time (latest slot) | {rpc.get('block_time', 'n/a')} |")
    lines.append("")

    # 2. Validators
    lines.append("## 2. Validators")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Active validators | {rpc.get('active_validators', 'n/a')} |")
    lines.append(f"| Delinquent validators | {rpc.get('delinquent_validators', 'n/a')} |")
    lines.append(f"| Total staked | {_fmt_sol(rpc.get('total_staked_sol'))} |")
    dist = rpc.get("stake_distribution") or {}
    if dist:
        lines.append(f"| Active stake | {_fmt_sol(dist.get('active_sol'))} |")
        lines.append(f"| Delinquent stake | {_fmt_sol(dist.get('delinquent_sol'))} |")
    lines.append("")
    top_v = rpc.get("top_validators") or []
    if top_v:
        lines.append("**Top validators by stake:**")
        lines.append("")
        lines.append("| # | Validator | Stake | Commission |")
        lines.append("|---|-----------|-------|------------|")
        for i, v in enumerate(top_v, 1):
            lines.append(f"| {i} | `{v['pubkey'][:12]}…` | {_fmt_sol(v.get('stake_sol'))} | {v.get('commission')}% |")
        lines.append("")

    # 3. Economic indicators
    lines.append("## 3. Economic Indicators")
    lines.append("")
    lines.append("| Indicator | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| SOL price (USDT) | ${price.get('sol_usdt', 'n/a')} |")
    if price.get("sol_24h_change") is not None:
        lines.append(f"| SOL 24h change | {price['sol_24h_change']:.2f}% |")
        lines.append(f"| 24h high / low | ${price.get('sol_24h_high')} / ${price.get('sol_24h_low')} |")
        lines.append(f"| 24h volume | {_fmt_usd(price.get('sol_24h_volume_usdt'))} |")
    lines.append(f"| Chain TVL (DeFiLlama) | {_fmt_usd(dl.get('chain_tvl_usd'))} |")
    lines.append(f"| Protocol mcap (DeFiLlama) | {_fmt_usd(dl.get('protocol_mcap_usd'))} |")
    if sc.get("stablecoin_total"):
        lines.append(f"| Stablecoin total circulation (SOL) | {_fmt_usd(sc['stablecoin_total'])} |")
    lines.append(f"| SOL supply (total) | {_fmt_sol(rpc.get('supply', {}).get('total'))} |" if rpc.get("supply", {}).get("total") else "| SOL supply | n/a |")
    lines.append(f"| SOL circulating | {_fmt_sol(rpc.get('supply', {}).get('circulating'))} |" if rpc.get("supply", {}).get("circulating") else "| SOL circulating | n/a |")
    lines.append("")

    # 4. Data sources
    lines.append("## 4. Data Sources")
    lines.append("")
    lines.append("- **On-chain:** Solana RPC (`getSlot`, `getEpochInfo`, `getRecentPerformanceSamples`, `getVoteAccounts`, `getSupply`)")
    lines.append("- **TVL:** DeFiLlama (`api.llama.fi/v2/chains`, `protocol/solana`)")
    lines.append("- **Price/volume:** Gate.io spot ticker (`SOL_USDT`)")
    lines.append("- **Stablecoins:** DeFiLlama stablecoin charts (Solana)")
    lines.append("")

    # 5. Methodology
    lines.append("## 5. Methodology & Automation")
    lines.append("")
    lines.append("- Data refresh: configurable interval via scheduled GitHub Actions (default daily 04:00 UTC) + manual dispatch")
    lines.append("- RPC snapshot runs on an overseas runner; off-chain sources run anywhere")
    lines.append("- Anomaly detection: threshold-based alerts on price moves >10%, TPS <1500, validator delinquency >10%")
    lines.append("- Outputs: this Markdown report, machine-readable JSON, interactive HTML dashboard")

    return "\n".join(lines)


if __name__ == "__main__":
    # load latest json report
    files = sorted(REPORTS.glob("solana_ecosystem_*.json"))
    if not files:
        print("no report json found; run src/collector.py first")
        sys.exit(1)
    report = json.loads(files[-1].read_text(encoding="utf-8"))
    md = render_markdown(report)
    date_str = report.get("generated_at", "")[:10]
    out = REPORTS / f"solana_ecosystem_{date_str}.md"
    out.write_text(md, encoding="utf-8")
    print(f"written: {out}")
