"""Solana Ecosystem Data Collector

Fetches on-chain + off-chain data for the Solana ecosystem report.
Local-run friendly (DeFiLlama + Gate.io reachable from CN); Solana RPC
methods run from GitHub Actions (overseas runner) via scripts/rpc_collect.py.

Output: reports/solana_ecosystem_<date>.json + .md + .html
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"

UA = {"User-Agent": "Mozilla/5.0 solana-ecosystem-dashboard/1.0"}


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "{}")


def fetch_defillama():
    """DeFiLlama: chain TVL, protocol mcap, stablecoin supply."""
    data = {}
    try:
        chains = http_json("https://api.llama.fi/v2/chains")
        for c in chains:
            if c.get("name", "").lower() == "solana":
                data["chain_tvl_usd"] = round(c.get("tvl", 0), 2)
                break
    except Exception as e:
        data["chain_tvl_error"] = str(e)
    try:
        proto = http_json("https://api.llama.fi/protocol/solana")
        data["protocol_mcap_usd"] = proto.get("mcap")
        data["protocol_chain_tvls"] = proto.get("chainTvls", {}).get("Solana")
        data["protocol_current_tvls"] = proto.get("currentChainTvls", {}).get("Solana")
    except Exception as e:
        data["protocol_error"] = str(e)
    return data


def fetch_gateio():
    """Gate.io spot ticker for SOL (reachable from CN)."""
    try:
        rows = http_json("https://api.gateio.ws/api/v4/spot/tickers?currency_pair=SOL_USDT")
        if isinstance(rows, list) and rows:
            t = rows[0]
            return {
                "sol_usdt": float(t.get("last", 0)),
                "sol_24h_change": float(t.get("change_percentage", 0)),
                "sol_24h_high": float(t.get("high_24h", 0)),
                "sol_24h_low": float(t.get("low_24h", 0)),
                "sol_24h_volume_usdt": float(t.get("quote_volume", 0)),
            }
    except Exception as e:
        return {"price_error": str(e)}
    return {}


def fetch_defillama_stablecoins():
    """Stablecoin supply on Solana (best-effort)."""
    try:
        rows = http_json("https://stablecoins.llama.fi/stablecoincharts/Solana?stablecoin=1")
        if isinstance(rows, list) and rows:
            last = rows[-1]
            return {"stablecoin_total": last.get("totalCirculationUSD", last.get("total", 0))}
    except Exception as e:
        return {"stablecoin_error": str(e)}
    return {}


def load_rpc_data():
    """Load RPC snapshot produced by GitHub Actions (scripts/rpc_collect.py)."""
    rpc_file = ROOT / "reports" / "rpc_snapshot.json"
    if rpc_file.exists():
        try:
            return json.loads(rpc_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def detect_anomalies(data: dict) -> list[dict]:
    """Simple threshold-based anomaly detection on key metrics."""
    anomalies = []
    price = data.get("price", {}).get("sol_usdt")
    if price and abs(data.get("price", {}).get("sol_24h_change", 0)) > 10:
        anomalies.append({
            "metric": "SOL price",
            "severity": "warning",
            "detail": f"24h change {data['price']['sol_24h_change']:.1f}% (threshold 10%)",
        })
    if data.get("rpc"):
        rpc = data["rpc"]
        tps = rpc.get("tps")
        if tps is not None and tps < 1500:
            anomalies.append({
                "metric": "TPS",
                "severity": "info",
                "detail": f"TPS {tps:.0f} below 1500",
            })
        deliq = rpc.get("delinquent_validators")
        total_v = rpc.get("active_validators")
        if deliq is not None and total_v and deliq / max(total_v, 1) > 0.1:
            anomalies.append({
                "metric": "Validator delinquency",
                "severity": "warning",
                "detail": f"{deliq}/{total_v} delinquent (>10%)",
            })
    return anomalies


def collect() -> dict:
    dl = fetch_defillama()
    price = fetch_gateio()
    sc = fetch_defillama_stablecoins()
    rpc = load_rpc_data()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "solana-ecosystem-dashboard",
        "defillama": dl,
        "price": price,
        "stablecoins": sc,
        "rpc": rpc,
        "anomalies": [],
    }
    report["anomalies"] = detect_anomalies(report)

    OUT.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_path = OUT / f"solana_ecosystem_{date_str}.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report, json_path


if __name__ == "__main__":
    report, path = collect()
    print(f"written: {path}")
    print(json.dumps({k: v for k, v in report.items() if k != 'rpc'}, ensure_ascii=False, indent=1)[:800])
    if report.get("rpc"):
        print("rpc keys:", list(report["rpc"].keys()))
