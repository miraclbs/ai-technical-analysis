#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ai_ready_tech_engine.py
BTCUSDT.P (Binance Futures) için AI-ready teknik analiz verisi üretir.

Timeframes ve mum sayıları:
- 4h: 20
- 1h: 30
- 15m: 40

Çıktı (her timeframe):
- candles: Son N mum için OHLCV + SMA/EMA(50/100/200) + RSI(14) + MACD(12/26/9)
           + ATR(14) + OBV + change_pct(%) + trend_flags + candle pattern
- summary: key_levels (ATR bazlı zone & tüm seviyeler), indicators, patterns, metrics

Not: Bu betik "analiz/öneri" üretmez; yalnızca modeli besleyecek veriyi JSON olarak hazırlar.
"""

import json
import os
from math import atan
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import ccxt
from supabase import create_client, Client
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


# =========================
#  SUPABASE CONFIGURATION
# =========================
def get_supabase_client() -> Client:
    """
    Supabase bağlantısı kurar.
    Çevre değişkenlerinden SUPABASE_URL ve SUPABASE_KEY okur.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "Supabase bağlantı bilgileri eksik!\n"
            "Lütfen SUPABASE_URL ve SUPABASE_KEY çevre değişkenlerini ayarlayın."
        )
    
    return create_client(url, key)


def clear_table(table_name: str = "btc_analysis") -> None:
    """
    Tablodaki tüm verileri siler.
    
    Args:
        table_name: Temizlenecek tablo adı
    """
    supabase = get_supabase_client()
    
    # Tüm kayıtları al ve sil
    try:
        # Önce tüm ID'leri al
        response = supabase.table(table_name).select("id").execute()
        
        if response.data and len(response.data) > 0:
            # Her kaydı sil
            for row in response.data:
                supabase.table(table_name).delete().eq('id', row['id']).execute()
            print(f"🗑️  '{table_name}' tablosundan {len(response.data)} kayıt silindi.")
        else:
            print(f"ℹ️  '{table_name}' tablosu zaten boş.")
    except Exception as e:
        print(f"⚠️  Tablo temizleme hatası: {e}")


def save_to_supabase(data: dict, table_name: str = "btc_analysis") -> dict:
    """
    Analiz verisini Supabase'e kaydeder.
    Önce tabloyu temizler, sonra yeni veriyi ekler.
    
    Args:
        data: Kaydedilecek JSON verisi
        table_name: Hedef tablo adı (varsayılan: btc_analysis)
    
    Returns:
        Supabase'den dönen response
    """
    supabase = get_supabase_client()
    
    # Önce tabloyu temizle
    clear_table(table_name)
    
    # Yeni veriyi kaydet
    response = supabase.table(table_name).insert(data).execute()
    
    return response


# =========================
#       INDICATORS
# =========================
def sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=length, min_periods=length).mean()

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False, min_periods=length).mean()

def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/length, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/length, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(length, min_periods=length).mean()

def obv(df: pd.DataFrame) -> pd.Series:
    delta = np.sign(df["close"].diff().fillna(0.0))
    return (delta * df["volume"]).cumsum()

def candle_pattern_row(o, h, l, c):
    body = abs(c - o)
    rng = max(h - l, 1e-9)
    upper = h - max(c, o)
    lower = min(c, o) - l
    if body / rng < 0.1:
        return "doji"
    if lower > 2 * body and upper < body:
        return "hammer"
    if upper > 2 * body and lower < body:
        return "shooting_star"
    return "normal"

def detect_multi_bar_pattern(df_tail: pd.DataFrame):
    """Basit morning/evening star tahmini (son 3 mum)."""
    if len(df_tail) < 3:
        return None
    o1, h1, l1, c1 = df_tail.iloc[-3][["open","high","low","close"]]
    o2, h2, l2, c2 = df_tail.iloc[-2][["open","high","low","close"]]
    o3, h3, l3, c3 = df_tail.iloc[-1][["open","high","low","close"]]

    # Morning star (downtrend sonrası varsaymaz, yalın form)
    cond_morning = (c1 < o1) and (abs(c2 - o2) / max(h2 - l2, 1e-9) < 0.3) and (c3 > o3) and (c3 > (o1 + c1)/2)
    if cond_morning:
        return "morning_star"
    # Evening star
    cond_evening = (c1 > o1) and (abs(c2 - o2) / max(h2 - l2, 1e-9) < 0.3) and (c3 < o3) and (c3 < (o1 + c1)/2)
    if cond_evening:
        return "evening_star"
    return None


# =========================
#       DATA UTILS
# =========================
def _float(x):
    return None if pd.isna(x) else float(x)

def fetch_ohlcv(symbol: str, timeframe: str, need: int) -> pd.DataFrame:
    """İndikatörler için yeterli geçmişi almak adına ekstra buffer çeker."""
    buffer = max(210, need + 200)  # SMA200/EMA200 için güvenli buffer
    ex = ccxt.binance({"options": {"defaultType": "future"}, "enableRateLimit": True})
    rows = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=buffer)
    df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    return df

def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for L in (50, 100, 200):
        d[f"sma{L}"] = sma(d["close"], L)
        d[f"ema{L}"] = ema(d["close"], L)
    d["rsi14"] = rsi(d["close"], 14)
    d["macd"], d["macd_signal"], d["macd_hist"] = macd(d["close"])
    d["atr14"] = atr(d, 14)
    d["obv"] = obv(d)
    d["change_pct"] = (d["close"] - d["open"]) / d["open"] * 100.0
    d["above_sma200"] = d["close"] > d["sma200"]
    d["above_ema200"] = d["close"] > d["ema200"]
    d["pattern"] = [candle_pattern_row(o, h, l, c) for o,h,l,c in zip(d["open"], d["high"], d["low"], d["close"])]
    return d

def recent_candles_json(df: pd.DataFrame, last_n: int):
    tail = df.dropna().tail(last_n)
    out = []
    for ts, r in tail.iterrows():
        out.append({
            "timestamp": ts.isoformat().replace("+00:00", "Z"),
            "open": _float(r["open"]),
            "high": _float(r["high"]),
            "low": _float(r["low"]),
            "close": _float(r["close"]),
            "volume": _float(r["volume"]),
            "sma50": _float(r["sma50"]), "sma100": _float(r["sma100"]), "sma200": _float(r["sma200"]),
            "ema50": _float(r["ema50"]), "ema100": _float(r["ema100"]), "ema200": _float(r["ema200"]),
            "rsi14": _float(r["rsi14"]),
            "macd": _float(r["macd"]), "macd_signal": _float(r["macd_signal"]), "macd_hist": _float(r["macd_hist"]),
            "atr14": _float(r["atr14"]),
            "obv": _float(r["obv"]),
            "change_pct": _float(r["change_pct"]),
            "trend_flags": {
                "above_sma200": bool(r["above_sma200"]),
                "above_ema200": bool(r["above_ema200"])
            },
            "pattern": r["pattern"]
        })
    return out


# =========================
#  SUPPORT/RESISTANCE & SUMMARIES
# =========================
def cluster_levels(levels: list, zone_width: float):
    """ATR tabanlı zone gruplayıcı: yakın seviyeleri tek cluster yapar (merkez = medyan)."""
    if not levels:
        # hiçbir seviye bulunmazsa boş merkez ve cluster döndür
        return [], []


    levels = sorted(levels)
    clusters = [[levels[0]]]
    for lvl in levels[1:]:
        if abs(lvl - clusters[-1][-1]) <= zone_width:
            clusters[-1].append(lvl)
        else:
            clusters.append([lvl])
    # cluster merkezlerini dön
    centers = [float(np.median(c)) for c in clusters]
    return centers, clusters

def detect_all_levels(df: pd.DataFrame, window: int = 10) -> dict:
    """Swing high/low ile tüm aday seviyeleri çıkarır (ham listeler)."""
    highs, lows = [], []
    for i in range(window, len(df) - window):
        hh = df["high"].iloc[i]
        ll = df["low"].iloc[i]
        if hh == df["high"].iloc[i - window:i + window + 1].max():
            highs.append(hh)
        if ll == df["low"].iloc[i - window:i + window + 1].min():
            lows.append(ll)
    return {"highs": highs, "lows": lows}

def grade_levels_by_volume(df: pd.DataFrame, levels: list, side: str, radius_mult: float = 0.5):
    """Seviye etrafında hacim ortalamasıyla ağırlık verip (strong/moderate/weak) sınıflandır."""
    if not levels or df.empty:
        return {"strong": [], "moderate": [], "weak": []}

    atr_now = float(df["atr14"].dropna().iloc[-1]) if df["atr14"].notna().any() else (df["high"]-df["low"]).mean()
    avg_vol = float(df["volume"].mean())
    strong, moderate, weak = [], [], []
    radius = max(atr_now * radius_mult, 1e-9)

    for lvl in levels:
        # Level çevresindeki mumların hacim ortalaması
        mask = (df["high"] >= lvl - radius) & (df["low"] <= lvl + radius)
        local_vol = float(df.loc[mask, "volume"].mean()) if mask.any() else 0.0
        # sınıflandırma
        if local_vol >= 1.5 * avg_vol:
            strong.append(lvl)
        elif local_vol >= 1.0 * avg_vol:
            moderate.append(lvl)
        else:
            weak.append(lvl)
    return {"strong": sorted(strong), "moderate": sorted(moderate), "weak": sorted(weak)}

def summarize_key_levels(df: pd.DataFrame, last_n: int):
    """ATR tabanlı zone, tüm seviyeler ve güç sınıflandırması üretir."""
    sub = df.dropna().tail(last_n + 200)  # last_n çevresinde bağlam olsun
    if sub.empty:
        return {
            "strong_support": [], "moderate_support": [], "weak_support": [],
            "strong_resistance": [], "moderate_resistance": [], "weak_resistance": [],
            "all_support_levels": [], "all_resistance_levels": []
        }

    mid_price = float(sub["close"].iloc[-1])
    atr_now = float(sub["atr14"].iloc[-1]) if sub["atr14"].notna().any() else float((sub["high"]-sub["low"]).mean())
    raw = detect_all_levels(sub, window=10)

    # ATR'ye göre cluster (zone)
    zone_width = max(atr_now * 1.0, 1e-9)
    res_centers, res_clusters = cluster_levels(raw.get("highs", []), zone_width)
    sup_centers, sup_clusters = cluster_levels(raw.get("lows", []), zone_width)


    # Fiyatın üstü/altı olarak ayır
    all_res = sorted([lvl for lvl in res_centers if lvl > mid_price])
    all_sup = sorted([lvl for lvl in sup_centers if lvl < mid_price])

    # Güce göre sınıflandır (hacim temelli)
    res_rank = grade_levels_by_volume(sub, all_res, side="resistance", radius_mult=0.5)
    sup_rank = grade_levels_by_volume(sub, all_sup, side="support", radius_mult=0.5)

    return {
        "strong_support": sup_rank["strong"],
        "moderate_support": sup_rank["moderate"],
        "weak_support": sup_rank["weak"],
        "strong_resistance": res_rank["strong"],
        "moderate_resistance": res_rank["moderate"],
        "weak_resistance": res_rank["weak"],
        "all_support_levels": all_sup,
        "all_resistance_levels": all_res
    }

def rsi_summary(df_tail: pd.DataFrame):
    r = df_tail["rsi14"].dropna()
    if len(r) < 3:
        return {"value": _float(r.iloc[-1]) if len(r) else None, "trend": None, "divergence": "none"}
    trend = "rising" if r.iloc[-1] > r.iloc[0] else "falling"
    div = "none"
    # basit divergence (son 3 bara bak)
    c = df_tail["close"].iloc[-3:]
    r3 = r.iloc[-3:]
    if c.iloc[-1] > c.iloc[0] and r3.iloc[-1] < r3.iloc[0]:
        div = "bearish"
    elif c.iloc[-1] < c.iloc[0] and r3.iloc[-1] > r3.iloc[0]:
        div = "bullish"
    return {"value": _float(r.iloc[-1]), "trend": trend, "divergence": div}

def macd_summary(df_tail: pd.DataFrame):
    m = df_tail[["macd","macd_signal","macd_hist"]].dropna()
    if m.empty:
        return {"histogram_trend": None, "crossover": None}
    hist_trend = "rising" if m["macd_hist"].iloc[-1] > m["macd_hist"].iloc[0] else "falling"
    cross = "bullish" if m["macd"].iloc[-1] > m["macd_signal"].iloc[-1] else "bearish"
    return {"histogram_trend": hist_trend, "crossover": cross}

def atr_summary(df_tail: pd.DataFrame):
    a = df_tail["atr14"].dropna()
    if a.empty:
        return {"value": None, "volatility_regime": None}
    val = float(a.iloc[-1])
    avg = float(a.mean())
    if val >= 1.25 * avg:
        regime = "high"
    elif val <= 0.75 * avg:
        regime = "low"
    else:
        regime = "moderate"
    return {"value": val, "volatility_regime": regime}

def volume_profile_summary(df_tail: pd.DataFrame):
    recent = df_tail["volume"].tail(min(len(df_tail), 20))
    if recent.empty:
        return {"support_volume": None, "resistance_volume": None}
    avg = float(df_tail["volume"].mean())
    sup = "high" if float(recent.mean()) > avg else "low"
    # Yalın yaklaşım: yükselişte dirençte hacim düşer (sıkışma), düşüşte artabilir vs.
    res = "low" if sup == "high" else "high"
    return {"support_volume": sup, "resistance_volume": res}

def patterns_summary(df_tail: pd.DataFrame):
    current = df_tail["pattern"].iloc[-1] if len(df_tail) else None
    multi = detect_multi_bar_pattern(df_tail)
    recent_high = float(df_tail["high"].max()) if len(df_tail) else None
    recent_low  = float(df_tail["low"].min()) if len(df_tail) else None

    # Breakout tespiti: son kapanış, son N en yüksek/düşüğün üstünde/altında mı?
    breakout_direction = None
    breakout_strength = None
    if len(df_tail):
        last_close = float(df_tail["close"].iloc[-1])
        atr_now = float(df_tail["atr14"].iloc[-1]) if df_tail["atr14"].notna().any() else float((df_tail["high"]-df_tail["low"]).mean())
        if last_close > recent_high:
            breakout_direction = "up"
            breakout_strength = "confirmed" if (last_close - recent_high) > 1.5 * atr_now / 100.0 * last_close else "weak"
        elif last_close < recent_low:
            breakout_direction = "down"
            breakout_strength = "confirmed" if (recent_low - last_close) > 1.5 * atr_now / 100.0 * last_close else "weak"

    confidence = "high" if current in ["hammer","shooting_star"] or multi in ["morning_star","evening_star"] else "medium"

    return {
        "current_pattern": current,
        "multi_bar_pattern": multi,
        "pattern_confidence": confidence,
        "key_breakout_levels": [recent_high, recent_low],
        "breakout_direction": breakout_direction,
        "breakout_strength": breakout_strength
    }

def metrics_summary(df_tail: pd.DataFrame):
    if len(df_tail) < 5:
        return {"trend_slope": None, "momentum_strength": None, "volume_anomaly": None}

    N = min(20, len(df_tail))
    close_change = float(df_tail["close"].iloc[-1] - df_tail["close"].iloc[-N])
    atr_now = float(df_tail["atr14"].iloc[-1]) if df_tail["atr14"].notna().any() else float((df_tail["high"]-df_tail["low"]).mean())
    slope = atan(close_change / max(N * atr_now, 1e-9))  # ATR ölçekli eğim

    # Momentum: RSI eğimi + MACD hist değişimi
    rsi_vals = df_tail["rsi14"].tail(N).dropna()
    macd_hist = df_tail["macd_hist"].tail(N).dropna()
    mom = None
    if len(rsi_vals) >= 2 and len(macd_hist) >= 2:
        rsi_up = rsi_vals.iloc[-1] - rsi_vals.iloc[0]
        hist_up = macd_hist.iloc[-1] - macd_hist.iloc[0]
        if rsi_up > 0 and hist_up > 0:
            mom = "rising"
        elif rsi_up < 0 and hist_up < 0:
            mom = "falling"
        else:
            mom = "mixed"

    # Hacim anomalisi
    last_vol = float(df_tail["volume"].iloc[-1])
    avg_vol = float(df_tail["volume"].mean())
    vol_anom = "yes" if last_vol > 1.5 * avg_vol else "no"

    return {"trend_slope": float(slope), "momentum_strength": mom, "volume_anomaly": vol_anom}

def enhanced_trend_analysis(df_tail: pd.DataFrame):
    """Gelişmiş trend analizi - farklı dönemlerde trend gücü."""
    if len(df_tail) < 50:
        return {"short_term": None, "medium_term": None, "long_term": None, "overall_direction": None}
    
    close = df_tail["close"]
    
    # Kısa vadeli trend (son 10 mum)
    short_trend = "bullish" if close.iloc[-1] > close.iloc[-10] else "bearish"
    short_strength = abs(close.iloc[-1] - close.iloc[-10]) / close.iloc[-10] * 100
    
    # Orta vadeli trend (son 30 mum)
    medium_trend = "bullish" if close.iloc[-1] > close.iloc[-30] else "bearish"
    medium_strength = abs(close.iloc[-1] - close.iloc[-30]) / close.iloc[-30] * 100
    
    # Uzun vadeli trend (son 50 mum)
    long_trend = "bullish" if close.iloc[-1] > close.iloc[-50] else "bearish"
    long_strength = abs(close.iloc[-1] - close.iloc[-50]) / close.iloc[-50] * 100
    
    # Genel yön - çoğunluk kuralı
    bullish_count = sum([short_trend == "bullish", medium_trend == "bullish", long_trend == "bullish"])
    overall = "bullish" if bullish_count >= 2 else "bearish"
    
    return {
        "short_term": {"direction": short_trend, "strength_pct": round(short_strength, 2)},
        "medium_term": {"direction": medium_trend, "strength_pct": round(medium_strength, 2)},
        "long_term": {"direction": long_trend, "strength_pct": round(long_strength, 2)},
        "overall_direction": overall,
        "trend_consistency": "consistent" if bullish_count in [0, 3] else "mixed"
    }


def fibonacci_levels(df_tail: pd.DataFrame):
    """Fibonacci retracement seviyeleri."""
    if len(df_tail) < 50:
        return None
    
    high = float(df_tail["high"].max())
    low = float(df_tail["low"].min())
    diff = high - low
    
    return {
        "swing_high": high,
        "swing_low": low,
        "fib_0.236": round(high - 0.236 * diff, 2),
        "fib_0.382": round(high - 0.382 * diff, 2),
        "fib_0.5": round(high - 0.5 * diff, 2),
        "fib_0.618": round(high - 0.618 * diff, 2),
        "fib_0.786": round(high - 0.786 * diff, 2)
    }


def price_action_signals(df_tail: pd.DataFrame):
    """Fiyat aksiyonu sinyalleri - Higher Highs/Lower Lows."""
    if len(df_tail) < 20:
        return None
    
    highs = df_tail["high"].tail(20)
    lows = df_tail["low"].tail(20)
    
    # Son 3 yüksek noktayı kontrol et
    recent_highs = highs.tail(10).nlargest(3).values
    higher_highs = recent_highs[0] > recent_highs[1] > recent_highs[2]
    
    # Son 3 düşük noktayı kontrol et
    recent_lows = lows.tail(10).nsmallest(3).values
    higher_lows = recent_lows[0] > recent_lows[1] > recent_lows[2]
    
    if higher_highs and higher_lows:
        signal = "strong_uptrend"
    elif not higher_highs and not higher_lows:
        signal = "strong_downtrend"
    elif higher_lows:
        signal = "bullish_structure"
    elif higher_highs:
        signal = "bearish_structure"
    else:
        signal = "ranging"
    
    return {
        "higher_highs": bool(higher_highs),
        "higher_lows": bool(higher_lows),
        "market_structure": signal
    }


def volume_analysis(df_tail: pd.DataFrame):
    """Detaylı hacim analizi."""
    if len(df_tail) < 20:
        return None
    
    volumes = df_tail["volume"]
    closes = df_tail["close"]
    
    avg_vol = float(volumes.mean())
    recent_avg = float(volumes.tail(5).mean())
    
    # Yükseliş/düşüş mumlarında hacim
    bullish_candles = df_tail[closes > df_tail["open"]]
    bearish_candles = df_tail[closes < df_tail["open"]]
    
    bullish_vol_avg = float(bullish_candles["volume"].mean()) if len(bullish_candles) > 0 else 0
    bearish_vol_avg = float(bearish_candles["volume"].mean()) if len(bearish_candles) > 0 else 0
    
    return {
        "avg_volume": round(avg_vol, 2),
        "recent_avg_volume": round(recent_avg, 2),
        "volume_trend": "increasing" if recent_avg > avg_vol else "decreasing",
        "bullish_volume_avg": round(bullish_vol_avg, 2),
        "bearish_volume_avg": round(bearish_vol_avg, 2),
        "volume_bias": "bullish" if bullish_vol_avg > bearish_vol_avg else "bearish"
    }


def moving_average_analysis(df_tail: pd.DataFrame):
    """Hareketli ortalama çapraz ve pozisyon analizi."""
    if len(df_tail) < 5:
        return None
    
    last = df_tail.iloc[-1]
    prev = df_tail.iloc[-2]
    
    current_price = float(last["close"])
    
    # MA pozisyonları
    ma_positions = {
        "price_vs_sma50": "above" if current_price > float(last["sma50"]) else "below",
        "price_vs_sma100": "above" if current_price > float(last["sma100"]) else "below",
        "price_vs_sma200": "above" if current_price > float(last["sma200"]) else "below",
        "sma50_vs_sma200": "above" if float(last["sma50"]) > float(last["sma200"]) else "below"
    }
    
    # Golden/Death Cross kontrolleri
    golden_cross = (float(last["sma50"]) > float(last["sma200"]) and 
                    float(prev["sma50"]) <= float(prev["sma200"]))
    death_cross = (float(last["sma50"]) < float(last["sma200"]) and 
                   float(prev["sma50"]) >= float(prev["sma200"]))
    
    return {
        "positions": ma_positions,
        "golden_cross": bool(golden_cross),
        "death_cross": bool(death_cross),
        "ma_alignment": "bullish" if ma_positions["sma50_vs_sma200"] == "above" else "bearish"
    }


def timeframe_summary(df: pd.DataFrame, last_n: int):
    """Genişletilmiş summary - daha fazla mum ile daha güçlü analiz."""
    # Daha fazla veri ile analiz yapmak için geniş tail al
    tail = df.dropna().tail(max(last_n, 100))  # En az 100 mum
    
    return {
        "key_levels": summarize_key_levels(df, last_n=last_n),
        "indicators": {
            "rsi": rsi_summary(tail),
            "macd": macd_summary(tail),
            "atr": atr_summary(tail),
            "volume_profile": volume_profile_summary(tail)
        },
        "patterns": patterns_summary(tail),
        "metrics": metrics_summary(tail),
        # Yeni gelişmiş analizler
        "trend_analysis": enhanced_trend_analysis(tail),
        "fibonacci": fibonacci_levels(tail),
        "price_action": price_action_signals(tail),
        "volume_analysis": volume_analysis(tail),
        "moving_averages": moving_average_analysis(tail)
    }


# =========================
#          MAIN
# =========================
def main():
    symbol = "BTC/USDT:USDT"  # Binance Futures sembolü (BTCUSDT.P)
    # Daha fazla mum çubuğu analiz et
    config = {"4h": 100, "1h": 150, "15m": 200}

    # Sadece summary için çıktı yapısı
    out = {
        "symbol": symbol,
        "as_of_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "timeframes": {}
    }

    for tf, need in config.items():
        print(f"\n🔄 {tf} timeframe analiz ediliyor... ({need} mum)")
        df = fetch_ohlcv(symbol, tf, need=need)
        df = enrich_indicators(df)
        summary = timeframe_summary(df, last_n=need)

        # Sadece summary'yi kaydet
        out["timeframes"][tf] = {
            "summary": summary
        }

    # JSON çıktısını göster
    print("\n" + "="*60)
    print("📊 ANALİZ SONUÇLARI")
    print("="*60)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    
    # Supabase'e kaydet
    try:
        response = save_to_supabase(out)
        print("\n✅ Veri Supabase'e başarıyla kaydedildi!")
        print(f"📝 Kayıt ID: {response.data[0]['id'] if response.data else 'N/A'}")
    except ValueError as e:
        print(f"\n⚠️ Supabase bağlantı hatası: {e}")
        print("Veri sadece console'a yazdırıldı.")
    except Exception as e:
        print(f"\n❌ Supabase kayıt hatası: {e}")
        print("Veri sadece console'a yazdırıldı.")


if __name__ == "__main__":
    main()
