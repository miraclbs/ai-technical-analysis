#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
crypto_data_multi_tf.py
BTCUSDT.P (Binance Futures) için:
4H: son 20 mum
1H: son 30 mum
15M: son 40 mum
Her mumda OHLCV + SMA/EMA(50/100/200) + RSI(14) + MACD(12/26/9) + ATR(14) + OBV + change_pct + trend flags + candle pattern
Veriler JSON olarak döndürülür, analiz yapılmaz.
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


# =========================
#  SUPABASE CONFIGURATION
# =========================
def get_supabase_client() -> Client:
    """Supabase bağlantısı kurar."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "Supabase bağlantı bilgileri eksik!\n"
            "Lütfen SUPABASE_URL ve SUPABASE_KEY çevre değişkenlerini ayarlayın."
        )
    
    return create_client(url, key)


def clear_table(table_name: str = "btc_raw_data") -> None:
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


def save_to_supabase(data: dict, table_name: str = "btc_raw_data") -> dict:
    """
    Ham veriyi Supabase'e kaydeder.
    Önce tabloyu temizler, sonra yeni veriyi ekler.
    
    Args:
        data: Kaydedilecek JSON verisi (tüm mumlar)
        table_name: Hedef tablo adı (varsayılan: btc_raw_data)
    
    Returns:
        Supabase'den dönen response
    """
    import sys
    print(f"🔄 Supabase bağlantısı kuruluyor...", flush=True)
    sys.stdout.flush()
    
    supabase = get_supabase_client()
    print(f"✅ Supabase bağlantısı başarılı!", flush=True)
    sys.stdout.flush()
    
    # Önce tabloyu temizle
    print(f"🗑️  '{table_name}' tablosu temizleniyor...", flush=True)
    sys.stdout.flush()
    clear_table(table_name)
    
    # Yeni veriyi kaydet
    print(f"💾 Yeni veri '{table_name}' tablosuna kaydediliyor...", flush=True)
    sys.stdout.flush()
    response = supabase.table(table_name).insert(data).execute()
    print(f"✅ Veri başarıyla kaydedildi! Kayıt sayısı: {len(response.data) if response.data else 0}", flush=True)
    sys.stdout.flush()
    
    return response


# === İNDİKATÖR FONKSİYONLARI === #
def sma(series, length):
    return series.rolling(window=length).mean()

def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def rsi(series, length=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/length, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/length, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26, signal=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def atr(df, length=14):
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(length).mean()

def obv(df):
    obv = np.sign(df["close"].diff().fillna(0)) * df["volume"]
    return obv.cumsum()

def detect_pattern(row):
    body = abs(row["close"] - row["open"])
    range_ = row["high"] - row["low"]
    upper_shadow = row["high"] - max(row["close"], row["open"])
    lower_shadow = min(row["close"], row["open"]) - row["low"]

    if range_ == 0:
        return "undefined"

    if body / range_ < 0.1:
        return "doji"
    elif lower_shadow > 2 * body and upper_shadow < body:
        return "hammer"
    elif upper_shadow > 2 * body and lower_shadow < body:
        return "shooting_star"
    else:
        return "normal"


# === VERİ ÇEKME === #
def get_ohlcv_df(symbol, timeframe, limit):
    # Birden fazla exchange dene (Binance bazı lokasyonları engelliyor)
    exchanges_to_try = [
        ("binance", {"options": {"defaultType": "future"}, "enableRateLimit": True}, "BTC/USDT:USDT"),
        ("okx", {"options": {"defaultType": "swap"}, "enableRateLimit": True}, "BTC/USDT:USDT"),
        ("bybit", {"enableRateLimit": True}, "BTC/USDT"),  # Bybit için spot market
        ("kraken", {"enableRateLimit": True}, "BTC/USDT"),
        ("kucoin", {"enableRateLimit": True}, "BTC/USDT")
    ]
    
    last_error = None
    for exchange_id, config, sym in exchanges_to_try:
        try:
            print(f"🔄 {exchange_id} deneniyor...", flush=True)
            exchange = getattr(ccxt, exchange_id)(config)
            data = exchange.fetch_ohlcv(sym, timeframe=timeframe, limit=limit + 200)
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df.set_index("timestamp", inplace=True)
            print(f"✅ {exchange_id} başarılı!", flush=True)
            return df
        except Exception as e:
            last_error = e
            print(f"⚠️ {exchange_id} failed: {str(e)[:150]}", flush=True)
            continue
    
    # Hiçbiri çalışmazsa hata fırlat
    raise Exception(f"Tüm exchange'ler başarısız oldu. Son hata: {last_error}")


def add_indicators(df):
    df["sma50"] = sma(df["close"], 50)
    df["sma100"] = sma(df["close"], 100)
    df["sma200"] = sma(df["close"], 200)
    df["ema50"] = ema(df["close"], 50)
    df["ema100"] = ema(df["close"], 100)
    df["ema200"] = ema(df["close"], 200)
    df["rsi14"] = rsi(df["close"], 14)
    macd_line, signal_line, hist = macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist
    df["atr14"] = atr(df, 14)
    df["obv"] = obv(df)
    df["change_pct"] = ((df["close"] - df["open"]) / df["open"]) * 100
    df["above_sma200"] = df["close"] > df["sma200"]
    df["above_ema200"] = df["close"] > df["ema200"]
    df["pattern"] = df.apply(detect_pattern, axis=1)
    return df


def _f(x):
    return None if pd.isna(x) else float(x)


def format_data(df, last_n):
    # En son mumdan başlayarak son N tanesini al
    tail = df.dropna().tail(last_n)
    candles = []
    for ts, row in tail.iterrows():
        # UTC'den Türkiye saatine (UTC+3) çevir
        tr_time = ts + pd.Timedelta(hours=3)
        
        candles.append({
            "timestamp": tr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "open": _f(row["open"]),
            "high": _f(row["high"]),
            "low": _f(row["low"]),
            "close": _f(row["close"]),
            "volume": _f(row["volume"]),
            "sma50": _f(row["sma50"]),
            "sma100": _f(row["sma100"]),
            "sma200": _f(row["sma200"]),
            "ema50": _f(row["ema50"]),
            "ema100": _f(row["ema100"]),
            "ema200": _f(row["ema200"]),
            "rsi14": _f(row["rsi14"]),
            "macd": _f(row["macd"]),
            "macd_signal": _f(row["macd_signal"]),
            "macd_hist": _f(row["macd_hist"]),
            "atr14": _f(row["atr14"]),
            "obv": _f(row["obv"]),
            "change_pct": _f(row["change_pct"]),
            "trend_flags": {
                "above_sma200": bool(row["above_sma200"]),
                "above_ema200": bool(row["above_ema200"])
            },
            "pattern": row["pattern"]
        })
    return candles


# === ANA === #
def main():
    symbol = "BTC/USDT:USDT"  # Binance Futures sembolü (BTCUSDT.P)
    timeframes = {
        "4h": 20,
        "1h": 30,
        "15m": 40
    }

    result = {
        "symbol": symbol,
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "timeframes": {}
    }

    for tf, n in timeframes.items():
        df = get_ohlcv_df(symbol, tf, limit=n)
        df = add_indicators(df)
        candles = format_data(df, last_n=n)
        result["timeframes"][tf] = candles

    # JSON çıktısı
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Dosyaya kaydet
    with open("btc_data_multi_tf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\n✅ Veriler 'btc_data_multi_tf.json' dosyasına kaydedildi.")
    
    # Supabase'e kaydet
    try:
        response = save_to_supabase(result)
        print("✅ Veri Supabase'e başarıyla kaydedildi!")
        print(f"📝 Kayıt ID: {response.data[0]['id'] if response.data else 'N/A'}")
    except ValueError as e:
        print(f"\n⚠️ Supabase bağlantı hatası: {e}")
        print("Veri sadece dosyaya kaydedildi.")
    except Exception as e:
        print(f"\n❌ Supabase kayıt hatası: {e}")
        print("Veri sadece dosyaya kaydedildi.")


if __name__ == "__main__":
    main()
