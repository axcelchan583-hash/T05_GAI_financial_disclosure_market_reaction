#!/usr/bin/env python3
"""Run a v4 peer-spillover main-effect pilot.

This is intentionally a pilot:

1. Uses the v4 X sample already built from strict IR/interactive QA events.
2. Fetches recent daily K-line data from Sina Finance for peer firms and SH index.
3. Computes peer CAR[-1,+1] with a market-model benchmark.
4. Runs simple OLS specifications for the interaction:

       PeerCAR_jt ~ ProductSimilarity_ij
                    + Specificity_it * ProductSimilarity_ij
                    + Event FE
                    + optional Peer FE

Formal work should replace the Sina public feed with CSMAR/Wind/RESSET returns.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
X_PATH = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_peer_event_x_same_industry_d_top10.csv"
OUT_DIR = ROOT / "results" / "v4_peer_spillover_main_effect_pilot"
CACHE_DIR = ROOT / "data" / "interim" / "sina_kline_cache_202602_202605"
DOC_PATH = ROOT / "docs" / "选题" / "24_v4_peer_spillover_main_effect_pilot_20260522.md"

SINA_URL = "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
SINA_JSONP_URL = "https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_test=/CN_MarketDataService.getKLineData"
MAX_PEER_RANK = int(os.environ.get("V4_MAX_PEER_RANK", "5"))


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def sina_symbol(code: str) -> str:
    code = code6(code)
    if code.startswith(("6", "5", "9")) and not code.startswith(("8", "9")):
        return f"sh{code}"
    if code.startswith(("8", "9")):
        return f"bj{code}"
    return f"sz{code}"


def make_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://finance.sina.com.cn/",
        }
    )
    return session


def parse_sina_payload(text: str) -> list[dict[str, object]]:
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    match = re.search(r"var\s+_test=\((.*)\);?\s*$", text, flags=re.S)
    if match:
        return json.loads(match.group(1))
    # The JSONP endpoint can prepend a small redirect script comment.
    bracket = text.find("[")
    end = text.rfind("]")
    if bracket >= 0 and end > bracket:
        return json.loads(text[bracket : end + 1])
    raise ValueError(f"Unable to parse Sina payload: {text[:120]}")


def frame_from_sina_data(data: list[dict[str, object]], cache_path: Path) -> pd.DataFrame:
    if not data:
        out = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume", "ret"])
        out.to_csv(cache_path, index=False)
        return out
    out = pd.DataFrame(data)
    out = out.rename(columns={"day": "date"})
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=["date", "close"]).sort_values("date")
    out["ret"] = out["close"].pct_change()
    out = out.dropna(subset=["ret"]).reset_index(drop=True)
    out.to_csv(cache_path, index=False)
    return out


def fetch_sina_kline(symbol: str, session: requests.Session, datalen: int = 520) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{symbol}.csv"
    if cache_path.exists():
        try:
            cached = pd.read_csv(cache_path)
            if not cached.empty:
                cached["date"] = pd.to_datetime(cached["date"])
                return cached
        except Exception:
            pass

    params = {"symbol": symbol, "scale": "240", "ma": "no", "datalen": str(datalen)}
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            resp = session.get(SINA_URL, params=params, timeout=4)
            resp.raise_for_status()
            return frame_from_sina_data(parse_sina_payload(resp.text), cache_path)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            try:
                resp = session.get(SINA_JSONP_URL, params=params, timeout=6)
                resp.raise_for_status()
                return frame_from_sina_data(parse_sina_payload(resp.text), cache_path)
            except Exception as fallback_exc:  # noqa: BLE001
                last_error = fallback_exc
            time.sleep(0.15 + attempt * 0.25)

    error_path = CACHE_DIR / f"{symbol}.error.json"
    error_path.write_text(json.dumps({"symbol": symbol, "error": str(last_error)}, ensure_ascii=False), encoding="utf-8")
    return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume", "ret"])


def load_x_sample() -> pd.DataFrame:
    df = pd.read_csv(X_PATH, dtype={"focal_code": str, "peer_code": str})
    df["peer_code"] = df["peer_code"].map(code6)
    df["focal_code"] = df["focal_code"].map(code6)
    df["raw_event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    for col in ["specificity", "product_similarity", "x_specificity_similarity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["peer_rank"] = pd.to_numeric(df["peer_rank"], errors="coerce")
    df = df[df["peer_rank"] <= MAX_PEER_RANK].copy()
    df = df[df["raw_event_date"].notna() & df["peer_code"].ne("")].copy()
    df["event_id"] = df["event_id"].astype(str)
    return df


def fetch_returns_for_sample(x: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    session = make_session()
    mkt = fetch_sina_kline("sh000001", session=session, datalen=620)
    mkt = mkt[["date", "ret"]].rename(columns={"ret": "mkt_ret"})
    mkt = mkt.dropna().sort_values("date")

    rows = []
    symbols = sorted({sina_symbol(code) for code in x["peer_code"].dropna().unique()})
    print(f"Fetching/reading Sina daily K-line for {len(symbols)} peer symbols; max_peer_rank={MAX_PEER_RANK}", flush=True)
    for idx, symbol in enumerate(symbols, start=1):
        kline = fetch_sina_kline(symbol, session=session, datalen=620)
        if not kline.empty:
            code = symbol[2:]
            tmp = kline[["date", "ret", "close", "volume"]].copy()
            tmp["peer_code"] = code
            tmp["sina_symbol"] = symbol
            rows.append(tmp)
        if idx % 25 == 0:
            print(f"  {idx}/{len(symbols)} symbols processed", flush=True)
        time.sleep(0.01)

    stock = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    return stock, mkt


def choose_event_date(raw_date: pd.Timestamp, after_close: bool, trading_dates: list[pd.Timestamp]) -> pd.Timestamp | None:
    if pd.isna(raw_date):
        return None
    dates = [d for d in trading_dates if d > raw_date] if after_close else [d for d in trading_dates if d >= raw_date]
    return dates[0] if dates else None


def compute_peer_car(x: pd.DataFrame, stock: pd.DataFrame, mkt: pd.DataFrame) -> pd.DataFrame:
    if stock.empty or mkt.empty:
        return pd.DataFrame()
    ret = stock.merge(mkt, on="date", how="inner").dropna(subset=["ret", "mkt_ret"])
    trading_dates = sorted(mkt["date"].dropna().unique())
    date_index = {d: i for i, d in enumerate(trading_dates)}
    ret_by_peer = {code: sub.sort_values("date") for code, sub in ret.groupby("peer_code")}

    out = []
    for _, ev in x.iterrows():
        peer = ev["peer_code"]
        if peer not in ret_by_peer:
            continue
        raw_date = ev["raw_event_date"]
        event_date = choose_event_date(raw_date, bool(ev.get("any_after_close", False) or ev.get("any_weekend_answer", False)), trading_dates)
        if event_date is None or event_date not in date_index:
            continue
        idx = date_index[event_date]
        if idx < 80:
            continue
        est_dates = set(trading_dates[max(0, idx - 220) : max(0, idx - 20)])
        win_dates = set(trading_dates[max(0, idx - 1) : min(len(trading_dates), idx + 2)])
        firm_ret = ret_by_peer[peer]
        est = firm_ret[firm_ret["date"].isin(est_dates)]
        win = firm_ret[firm_ret["date"].isin(win_dates)]
        if len(est) < 80 or len(win) < 2:
            continue
        xmat = np.column_stack([np.ones(len(est)), est["mkt_ret"].to_numpy()])
        y = est["ret"].to_numpy()
        alpha, beta = np.linalg.lstsq(xmat, y, rcond=None)[0]
        win = win.copy()
        win["abret"] = win["ret"] - (alpha + beta * win["mkt_ret"])
        car = float(win["abret"].sum())
        out.append(
            {
                **ev.to_dict(),
                "event_date_for_car": pd.Timestamp(event_date).strftime("%Y-%m-%d"),
                "estimation_obs": len(est),
                "event_window_obs": len(win),
                "peer_alpha": float(alpha),
                "peer_beta": float(beta),
                "peer_car_m1_p1": car,
                "peer_abs_car_m1_p1": abs(car),
                "peer_raw_return_m1_p1": float(win["ret"].sum()),
                "mkt_return_m1_p1": float(win["mkt_ret"].sum()),
            }
        )
    return pd.DataFrame(out)


def regression_row(label: str, formula: str, df: pd.DataFrame, cluster: str = "event_id") -> dict[str, object]:
    data = df.copy()
    model = smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups": data[cluster]})
    term = "x_specificity_similarity"
    return {
        "model": label,
        "formula": formula,
        "coef_x": model.params.get(term, np.nan),
        "se_x_cluster_event": model.bse.get(term, np.nan),
        "t_x": model.tvalues.get(term, np.nan),
        "p_x": model.pvalues.get(term, np.nan),
        "nobs": int(model.nobs),
        "r2": float(model.rsquared),
        "events": data["event_id"].nunique(),
        "peers": data["peer_code"].nunique(),
    }


def run_regressions(car: pd.DataFrame) -> pd.DataFrame:
    data = car.dropna(subset=["peer_car_m1_p1", "product_similarity", "x_specificity_similarity"]).copy()
    data["event_id_cat"] = data["event_id"].astype("category")
    data["peer_code_cat"] = data["peer_code"].astype("category")
    data["peer_rank"] = pd.to_numeric(data["peer_rank"], errors="coerce")

    specs = [
        (
            "M1_no_fe",
            "peer_car_m1_p1 ~ product_similarity + x_specificity_similarity",
        ),
        (
            "M2_event_fe",
            "peer_car_m1_p1 ~ product_similarity + x_specificity_similarity + C(event_id_cat)",
        ),
        (
            "M3_event_peer_fe",
            "peer_car_m1_p1 ~ product_similarity + x_specificity_similarity + C(event_id_cat) + C(peer_code_cat)",
        ),
        (
            "M4_event_fe_rank_control",
            "peer_car_m1_p1 ~ product_similarity + x_specificity_similarity + peer_rank + C(event_id_cat)",
        ),
    ]
    rows = []
    for label, formula in specs:
        try:
            rows.append(regression_row(label, formula, data))
        except Exception as exc:  # noqa: BLE001
            rows.append({"model": label, "formula": formula, "error": str(exc), "nobs": len(data)})
    return pd.DataFrame(rows)


def run_spread_test(car: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = car.copy()
    data["peer_rank"] = pd.to_numeric(data["peer_rank"], errors="coerce")
    max_rank = int(data["peer_rank"].max()) if data["peer_rank"].notna().any() else 0
    if max_rank >= 8:
        high_cutoff = 3
        low_cutoff = 8
    else:
        high_cutoff = 2
        low_cutoff = max(3, max_rank - 1)
    high = (
        data[data["peer_rank"] <= high_cutoff]
        .groupby("event_id", as_index=False)
        .agg(high_peer_car=("peer_car_m1_p1", "mean"))
    )
    low = (
        data[data["peer_rank"] >= low_cutoff]
        .groupby("event_id", as_index=False)
        .agg(low_peer_car=("peer_car_m1_p1", "mean"))
    )
    event_info = (
        data.groupby("event_id", as_index=False)
        .agg(
            focal_code=("focal_code", "first"),
            focal_name=("focal_name", "first"),
            event_date_for_car=("event_date_for_car", "first"),
            specificity=("specificity", "first"),
            obs=("peer_code", "count"),
        )
    )
    spread = event_info.merge(high, on="event_id", how="inner").merge(low, on="event_id", how="inner")
    spread["peer_spread_high_minus_low"] = spread["high_peer_car"] - spread["low_peer_car"]
    if len(spread) < 10:
        return spread, pd.DataFrame([{"note": "too few spread events", "n": len(spread)}])
    model = smf.ols("peer_spread_high_minus_low ~ specificity", data=spread).fit(cov_type="HC1")
    reg = pd.DataFrame(
        [
            {
                "term": "specificity",
                "coef": model.params.get("specificity", np.nan),
                "se_hc1": model.bse.get("specificity", np.nan),
                "t": model.tvalues.get("specificity", np.nan),
                "p": model.pvalues.get("specificity", np.nan),
                "nobs": int(model.nobs),
                "r2": float(model.rsquared),
            }
        ]
    )
    return spread, reg


def write_report(x: pd.DataFrame, stock: pd.DataFrame, mkt: pd.DataFrame, car: pd.DataFrame, reg: pd.DataFrame, spread: pd.DataFrame, spread_reg: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    car_stats = car["peer_car_m1_p1"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]) if not car.empty else pd.Series(dtype=float)
    x_stats = car["x_specificity_similarity"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]) if not car.empty else pd.Series(dtype=float)
    examples = (
        car.reindex(car["peer_car_m1_p1"].abs().sort_values(ascending=False).index)
        .head(20)[
            [
                "event_id",
                "focal_code",
                "focal_name",
                "event_date_for_car",
                "specificity",
                "peer_rank",
                "peer_code",
                "peer_name",
                "product_similarity",
                "x_specificity_similarity",
                "peer_car_m1_p1",
            ]
        ]
        if not car.empty
        else pd.DataFrame()
    )

    report = f"""# v4 主效应试跑：GenAI 披露具体性与竞品市场反应

日期：2026-05-22

## 1. 这次跑了什么

本次从 v4 X 样本继续向下跑一版主效应：

```text
PeerCAR_jt = beta1 ProductSimilarity_ij
           + beta2 Specificity_it × ProductSimilarity_ij
           + Event FE
           + Peer FE
           + error_ijt
```

其中 `PeerCAR_jt` 是产品市场 peer 公司在 focal 公司 GenAI 互动平台回复事件附近的 `CAR[-1,+1]`。

行情数据说明：

- 本次仅为 pilot，使用 Sina Finance 日 K 公开接口；
- 市场收益用上证指数 `sh000001`；
- 正式版本必须换成 CSMAR / Wind / RESSET 统一日收益；
- 事件日按互动回复是否盘后 / 周末顺延到下一交易日。
- 为了先跑出主效应，本次只使用 peer rank <= {MAX_PEER_RANK} 的事件-竞品观测。

## 2. 样本连接

| item | value |
|---|---:|
| X sample peer-event observations, rank <= {MAX_PEER_RANK} | {len(x)} |
| X sample events | {x['event_id'].nunique()} |
| X sample peer firms | {x['peer_code'].nunique()} |
| peer firms with fetched returns | {stock['peer_code'].nunique() if not stock.empty else 0} |
| market return date range | {mkt['date'].min().date() if not mkt.empty else 'NA'} to {mkt['date'].max().date() if not mkt.empty else 'NA'} |
| CAR-linked peer-event observations | {len(car)} |
| CAR-linked events | {car['event_id'].nunique() if not car.empty else 0} |
| CAR-linked peer firms | {car['peer_code'].nunique() if not car.empty else 0} |

## 3. Peer CAR 分布

| stat | peer_car_m1_p1 |
|---|---:|
| mean | {car_stats.get('mean', np.nan):.4f} |
| std | {car_stats.get('std', np.nan):.4f} |
| p10 | {car_stats.get('10%', np.nan):.4f} |
| p25 | {car_stats.get('25%', np.nan):.4f} |
| p50 | {car_stats.get('50%', np.nan):.4f} |
| p75 | {car_stats.get('75%', np.nan):.4f} |
| p90 | {car_stats.get('90%', np.nan):.4f} |
| min | {car_stats.get('min', np.nan):.4f} |
| max | {car_stats.get('max', np.nan):.4f} |

## 4. X 分布

| stat | Specificity × ProductSimilarity |
|---|---:|
| mean | {x_stats.get('mean', np.nan):.4f} |
| std | {x_stats.get('std', np.nan):.4f} |
| p10 | {x_stats.get('10%', np.nan):.4f} |
| p25 | {x_stats.get('25%', np.nan):.4f} |
| p50 | {x_stats.get('50%', np.nan):.4f} |
| p75 | {x_stats.get('75%', np.nan):.4f} |
| p90 | {x_stats.get('90%', np.nan):.4f} |
| min | {x_stats.get('min', np.nan):.4f} |
| max | {x_stats.get('max', np.nan):.4f} |

## 5. 主效应回归

{reg.to_markdown(index=False)}

解释边界：

- 主关注项是 `x_specificity_similarity`；
- `M2_event_fe` 是当前最应看的最小主规格；
- `M3_event_peer_fe` 加入 peer 固定效应，但 pilot 样本和公开行情下不宜过度解释；
- 所有标准误按 focal event 聚类。

## 6. Portfolio spread sanity check

构造：

```text
Top-rank peer portfolio CAR - low-rank peer portfolio CAR
```

其中 high peer 和 low peer 按本次保留的 rank 范围切分。

{spread_reg.to_markdown(index=False)}

## 7. CAR 最大的 peer-event 例子

{examples.to_markdown(index=False)}

## 8. 当前判断

这次回答的是“能不能一次性跑出主效应”。答案是：可以跑出，但只能作为 pilot。

如果 `M2_event_fe` 中 `x_specificity_similarity` 为正，初步含义是：

```text
同一个 GenAI 披露事件下，
披露越具体时，产品相似度越高的竞品反应越强。
```

如果系数不稳或符号与 portfolio spread 不一致，优先怀疑：

1. 互动平台事件太弱，市场未必定价；
2. `BusinessScope + MAINBUSSINESS` 竞品网络太粗；
3. Sina 公开行情和未复权 / 估计窗口处理只是 pilot；
4. 竞品反应方向可能混合了竞争威胁和行业机会。

下一步不应直接写结论，而应：

```text
先换 CSMAR/Wind 收益，再换年报业务章节 peer network，
然后看 M2_event_fe 和 portfolio spread 是否方向一致。
```

## 9. 输出文件

- `results/v4_peer_spillover_main_effect_pilot/v4_peer_event_with_car_sina.csv`
- `results/v4_peer_spillover_main_effect_pilot/v4_main_effect_regression_summary.csv`
- `results/v4_peer_spillover_main_effect_pilot/v4_peer_spread_by_event.csv`
- `results/v4_peer_spillover_main_effect_pilot/v4_peer_spread_regression.csv`
"""
    DOC_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    x = load_x_sample()
    stock, mkt = fetch_returns_for_sample(x)
    stock.to_csv(OUT_DIR / "v4_sina_peer_daily_returns_cache_panel.csv", index=False, encoding="utf-8-sig")
    mkt.to_csv(OUT_DIR / "v4_sina_sh000001_market_returns.csv", index=False, encoding="utf-8-sig")

    car = compute_peer_car(x, stock, mkt)
    car.to_csv(OUT_DIR / "v4_peer_event_with_car_sina.csv", index=False, encoding="utf-8-sig")

    reg = run_regressions(car)
    reg.to_csv(OUT_DIR / "v4_main_effect_regression_summary.csv", index=False, encoding="utf-8-sig")

    spread, spread_reg = run_spread_test(car)
    spread.to_csv(OUT_DIR / "v4_peer_spread_by_event.csv", index=False, encoding="utf-8-sig")
    spread_reg.to_csv(OUT_DIR / "v4_peer_spread_regression.csv", index=False, encoding="utf-8-sig")

    write_report(x, stock, mkt, car, reg, spread, spread_reg)

    print(f"X obs: {len(x)}")
    print(f"CAR-linked obs: {len(car)}")
    print(f"CAR-linked events: {car['event_id'].nunique() if not car.empty else 0}")
    print(f"CAR-linked peer firms: {car['peer_code'].nunique() if not car.empty else 0}")
    print(reg.to_string(index=False))
    print(f"wrote: {OUT_DIR}")
    print(f"wrote: {DOC_PATH}")


if __name__ == "__main__":
    main()
