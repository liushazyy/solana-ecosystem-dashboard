"""Interactive HTML dashboard generator (dark theme)."""
import html
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


def _card(title, value, sub="", accent="#4f8cff"):
    return f"""
    <div class="card">
      <div class="card-title">{html.escape(title)}</div>
      <div class="card-value" style="color:{accent}">{html.escape(str(value))}</div>
      {f'<div class="card-sub">{html.escape(str(sub))}</div>' if sub else ''}
    </div>"""


def render_html(report: dict) -> str:
    dl = report.get("defillama", {})
    price = report.get("price", {})
    sc = report.get("stablecoins", {})
    rpc = report.get("rpc", {})
    anomalies = report.get("anomalies", [])
    epoch = rpc.get("epoch_info") or {}
    ts = report.get("generated_at", "")

    anomaly_html = ""
    if anomalies:
        items = "".join(
            f'<div class="anomaly {a["severity"]}">⚠ {html.escape(a["metric"])}: {html.escape(a["detail"])}</div>'
            for a in anomalies
        )
        anomaly_html = f'<div class="anomaly-box"><h3>Anomaly Alerts</h3>{items}</div>'

    top_v = rpc.get("top_validators") or []
    if top_v:
        rows = "".join(
            f'<tr><td>{i}</td><td><code>{html.escape(v["pubkey"][:16])}…</code></td>'
            f'<td>{_fmt_usd(v.get("stake_sol"))}</td><td>{v.get("commission")}%</td></tr>'
            for i, v in enumerate(top_v, 1)
        )
        vtable = f"""<div class="card wide">
          <div class="card-title">Top Validators by Stake</div>
          <table><tr><th>#</th><th>Validator</th><th>Stake</th><th>Commission</th></tr>{rows}</table>
        </div>"""
    else:
        vtable = ""

    supply = rpc.get("supply", {})
    # build a simple SVG bar for staking distribution
    dist = rpc.get("stake_distribution") or {}
    active_sol = float(dist.get("active_sol") or 0)
    deliq_sol = float(dist.get("delinquent_sol") or 0)
    total = active_sol + deliq_sol
    if total > 0:
        aw = 100 * active_sol / total
        dw = 100 - aw
        dist_bar = f"""
        <div class="dist-bar">
          <div class="dist-seg" style="width:{aw:.1f}%;background:#22c55e" title="Active {_fmt_usd(active_sol)}"></div>
          <div class="dist-seg" style="width:{dw:.1f}%;background:#ef4444" title="Delinquent {_fmt_usd(deliq_sol)}"></div>
        </div>
        <div class="legend"><span class="dot" style="background:#22c55e"></span>Active {_fmt_usd(active_sol)} &nbsp;
        <span class="dot" style="background:#ef4444"></span>Delinquent {_fmt_usd(deliq_sol)}</div>"""
    else:
        dist_bar = "<p>No staking data</p>"

    price_val = price.get("sol_usdt", "n/a")
    change = price.get("sol_24h_change")
    change_str = f"{change:+.2f}%" if change is not None else ""
    change_color = "#22c55e" if (change or 0) >= 0 else "#ef4444"

    html_doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solana Ecosystem Dashboard</title>
<style>
:root {{ color-scheme: dark; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0b1220; color: #e2e8f0; font-family: 'Segoe UI', system-ui, sans-serif; padding: 24px; }}
h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
h2 {{ font-size: 1.15rem; margin: 28px 0 12px; color: #93c5fd; border-bottom: 1px solid #1e293b; padding-bottom: 6px; }}
.sub {{ color: #64748b; font-size: .85rem; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }}
.card {{ background: #111a2e; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; }}
.card.wide {{ grid-column: 1 / -1; }}
.card-title {{ color: #94a3b8; font-size: .8rem; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }}
.card-value {{ font-size: 1.5rem; font-weight: 700; }}
.card-sub {{ color: #64748b; font-size: .8rem; margin-top: 4px; }}
.anomaly-box {{ background: #1a1424; border: 1px solid #7c3aed; border-radius: 10px; padding: 14px 16px; margin: 18px 0; }}
.anomaly-box h3 {{ color: #c4b5fd; margin-bottom: 8px; font-size: 1rem; }}
.anomaly {{ padding: 6px 10px; border-radius: 6px; margin: 4px 0; font-size: .9rem; }}
.anomaly.warning {{ background: #451a03; color: #fdba74; }}
.anomaly.info {{ background: #0c4a6e; color: #7dd3fc; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: .9rem; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #1e293b; }}
th {{ color: #94a3b8; font-weight: 600; }}
code {{ background: #0b1220; padding: 2px 6px; border-radius: 4px; font-size: .85rem; }}
.dist-bar {{ display: flex; height: 18px; border-radius: 8px; overflow: hidden; margin: 10px 0; }}
.dist-seg {{ height: 100%; }}
.legend {{ font-size: .85rem; color: #94a3b8; }}
.dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }}
.footer {{ margin-top: 30px; color: #475569; font-size: .78rem; text-align: center; }}
@media (max-width: 600px) {{ body {{ padding: 14px; }} .card-value {{ font-size: 1.2rem; }} }}
</style></head><body>
<h1>Solana Ecosystem Dashboard</h1>
<div class="sub">Generated {html.escape(ts)} UTC &nbsp;·&nbsp; RPC: <code>{html.escape(str(rpc.get("endpoint","n/a")))}</code> &nbsp;·&nbsp; auto-updating</div>
{anomaly_html}
<h2>Network &amp; Market Overview</h2>
<div class="grid">
{_card("SOL Price", f"${price_val}", change_str, change_color)}
{_card("Chain TVL", _fmt_usd(dl.get("chain_tvl_usd")), "DeFiLlama")}
{_card("Protocol Market Cap", _fmt_usd(dl.get("protocol_mcap_usd")), "DeFiLlama")}
{_card("TPS (recent)", f"{float(rpc['tps']):.0f}" if rpc.get("tps") else "n/a", "performance sample")}
{_card("Slot", rpc.get("slot", "n/a"), f"epoch {epoch.get('epoch','n/a')} · {epoch.get('slotIndex','n/a')}/{epoch.get('slotsInEpoch','n/a')}")}
{_card("Active Validators", rpc.get("active_validators", "n/a"), f"{rpc.get('delinquent_validators',0)} delinquent")}
{_card("Total Staked", _fmt_usd(rpc.get("total_staked_sol")), "SOL")}
{_card("Stablecoin Supply", _fmt_usd(sc.get("stablecoin_total")), "on Solana") if sc.get("stablecoin_total") else _card("Stablecoin Supply", "n/a")}
{_card("SOL Supply", _fmt_usd(supply.get("total")), f"circulating {_fmt_usd(supply.get('circulating'))}" if supply.get("circulating") else "")}
{_card("24h Volume", _fmt_usd(price.get("sol_24h_volume_usdt")), "Gate.io SOL_USDT") if price.get("sol_24h_volume_usdt") else ""}
</div>
{vtable}
<h2>Staking Distribution</h2>
{dist_bar}
<div class="footer">Source: Solana RPC · DeFiLlama · Gate.io · Generated by solana-ecosystem-dashboard (open-source)</div>
</body></html>"""
    return html_doc


if __name__ == "__main__":
    import sys
    files = sorted(REPORTS.glob("solana_ecosystem_*.json"))
    if not files:
        print("no report json found; run src/collector.py first")
        sys.exit(1)
    report = json.loads(files[-1].read_text(encoding="utf-8"))
    out = REPORTS / "index.html"
    out.write_text(render_html(report), encoding="utf-8")
    print(f"written: {out}")
