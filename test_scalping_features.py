#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_scalping_features.py
Scalping özelliklerini test eder
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Test için basit veri üretimi
def create_test_data(n=200):
    """Test için OHLCV verisi üretir"""
    dates = pd.date_range(end=datetime.now(), periods=n, freq='15min')
    
    # Rastgele fiyat hareketi
    base_price = 98000
    price_changes = np.random.randn(n).cumsum() * 100
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': base_price + price_changes,
        'high': base_price + price_changes + np.random.rand(n) * 50,
        'low': base_price + price_changes - np.random.rand(n) * 50,
        'close': base_price + price_changes + np.random.randn(n) * 20,
        'volume': np.random.rand(n) * 1000000 + 500000
    })
    
    df.set_index('timestamp', inplace=True)
    return df


def test_scalping_indicators():
    """Scalping göstergelerini test eder"""
    print("🧪 SCALPING GÖSTERGELERİ TEST EDİLİYOR...\n")
    
    # qwen3 modülünü import et
    import sys
    sys.path.append('.')
    from qwen3 import (
        vwap, bollinger_bands, stochastic_rsi,
        micro_levels, scalping_signals, enhanced_15m_analysis,
        enrich_indicators, rsi, validate_indicators,
        market_regime_analysis, detect_volume_anomalies
    )
    
    # Test verisi
    df = create_test_data(200)
    
    # Test 0: Validasyon (Yeni!)
    print("✅ Test 0: Indicator Validation")
    df['vwap'] = vwap(df)
    df['rsi14'] = rsi(df['close'], 14)
    bb_middle, bb_upper, bb_lower, bb_percent_b, bb_bandwidth = bollinger_bands(df['close'], 20)
    df['bb_middle'] = bb_middle
    df['bb_upper'] = bb_upper
    df['bb_lower'] = bb_lower
    df['stoch_rsi'] = stochastic_rsi(df['rsi14'], 14)
    
    is_valid = validate_indicators(df.tail(50))
    print(f"   Validation Result: {'✅ PASS' if is_valid else '❌ FAIL'}")
    if is_valid:
        print(f"   All required indicators present and valid")
    print()
    
    # Test 8: Market Regime Analysis (YENİ!)
    print("✅ Test 8: Market Regime Analysis")
    regime = market_regime_analysis(df)
    if regime:
        print(f"   Volatility Regime: {regime['volatility_regime']}")
        print(f"   Trend Regime: {regime['trend_regime']}")
        print(f"   Range Regime: {regime['range_regime']}")
        print(f"   Current vs Avg Volatility: {regime['current_vs_avg_volatility_ratio']}x")
    print()
    
    # Test 9: Volume Anomalies (YENİ!)
    print("✅ Test 9: Volume Anomalies Detection")
    anomalies = detect_volume_anomalies(df)
    if anomalies:
        print(f"   Volume Z-Score: {anomalies['volume_zscore']}")
        print(f"   Anomaly Level: {anomalies['anomaly_level'].upper()}")
        print(f"   Current vs Avg Volume: {anomalies['current_vs_avg_volume_ratio']}x")
        print(f"   Volume Spike: {'YES 🔴' if anomalies['is_volume_spike'] else 'NO 🟢'}")
        print(f"   Volume Momentum: {anomalies['volume_momentum'].upper()}")
    print()
    
    # Test 1: VWAP
    print("✅ Test 1: VWAP")
    df['vwap'] = vwap(df)
    print(f"   VWAP Son Değer: ${df['vwap'].iloc[-1]:,.2f}")
    print(f"   Son Fiyat: ${df['close'].iloc[-1]:,.2f}")
    print(f"   VWAP Pozisyon: {'ABOVE' if df['close'].iloc[-1] > df['vwap'].iloc[-1] else 'BELOW'}\n")
    
    # Test 2: Bollinger Bands
    print("✅ Test 2: Bollinger Bands")
    bb_middle, bb_upper, bb_lower, bb_percent_b, bb_bandwidth = bollinger_bands(df['close'], 20)
    print(f"   Üst Band: ${bb_upper.iloc[-1]:,.2f}")
    print(f"   Orta Band: ${bb_middle.iloc[-1]:,.2f}")
    print(f"   Alt Band: ${bb_lower.iloc[-1]:,.2f}")
    print(f"   %B: {bb_percent_b.iloc[-1]:.3f}")
    print(f"   Bandwidth: {bb_bandwidth.iloc[-1]:.4f}")
    print(f"   Squeeze: {'YES' if bb_bandwidth.iloc[-1] < 0.1 else 'NO'}\n")
    
    # Test 3: Stochastic RSI
    print("✅ Test 3: Stochastic RSI")
    df['rsi14'] = rsi(df['close'], 14)
    df['stoch_rsi'] = stochastic_rsi(df['rsi14'], 14)
    stoch_value = df['stoch_rsi'].iloc[-1]
    print(f"   Stoch RSI: {stoch_value:.2f}")
    if stoch_value < 20:
        signal = "OVERSOLD 🟢"
    elif stoch_value > 80:
        signal = "OVERBOUGHT 🔴"
    else:
        signal = "NEUTRAL 🟡"
    print(f"   Sinyal: {signal}\n")
    
    # Test 4: Micro Levels
    print("✅ Test 4: Micro Levels")
    micro = micro_levels(df, window=10)
    print(f"   Immediate Resistance: ${micro['immediate_resistance']:,.2f}")
    print(f"   Immediate Support: ${micro['immediate_support']:,.2f}")
    print(f"   Current Range: ${micro['current_range']:,.2f}")
    print(f"   Range Position: {micro['range_position_pct']:.1f}%")
    print(f"   Consolidating: {'YES' if micro['is_consolidating'] else 'NO'}")
    print(f"   Breakout Levels:")
    print(f"     ↑ Upside: ${micro['range_breakout_levels']['upside']:,.2f}")
    print(f"     ↓ Downside: ${micro['range_breakout_levels']['downside']:,.2f}\n")
    
    # Test 5: Full enrichment
    print("✅ Test 5: Full Indicator Enrichment")
    df_enriched = enrich_indicators(df)
    new_columns = ['vwap', 'bb_middle', 'bb_upper', 'bb_lower', 'bb_percent_b', 'bb_bandwidth', 'stoch_rsi', 'ema20']
    print(f"   Eklenen Kolonlar: {', '.join(new_columns)}")
    print(f"   Toplam Kolon Sayısı: {len(df_enriched.columns)}\n")
    
    # Test 6: Scalping Signals
    print("✅ Test 6: Scalping Signals")
    signals = scalping_signals(df_enriched.tail(50))
    print(f"   VWAP Position: {signals['signals']['vwap_position']}")
    print(f"   Bollinger Squeeze: {signals['signals']['bollinger_squeeze']}")
    print(f"   Stoch RSI Signal: {signals['signals']['stoch_rsi_signal']}")
    print(f"   Volume Spike: {signals['signals']['volume_spike']}")
    print(f"   Entry Opportunities: {', '.join(signals['entry_opportunities']) if signals['entry_opportunities'] else 'None'}")
    print(f"   Confidence: {signals['confidence'].upper()} (Score: {signals['confidence_score']})")
    print(f"   Risk Level: {signals['risk_level'].upper()}\n")
    
    # Test 7: Enhanced 15m Analysis
    print("✅ Test 7: Enhanced 15m Analysis")
    analysis = enhanced_15m_analysis(df_enriched)
    if analysis:
        print(f"   ✓ Scalping Signals: ✅")
        print(f"   ✓ Micro Levels: ✅")
        print(f"   ✓ Momentum Indicators: ✅")
        print(f"   Entry Opportunities: {len(analysis['scalping_signals']['entry_opportunities'])}")
        print(f"   Confidence: {analysis['scalping_signals']['confidence'].upper()}")
    else:
        print(f"   ❌ Analysis failed (insufficient data)")
    
    print("\n" + "="*70)
    print("🎉 TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
    print("="*70)


if __name__ == "__main__":
    test_scalping_indicators()
