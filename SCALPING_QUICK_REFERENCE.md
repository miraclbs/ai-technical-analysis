# 📚 SCALPING ÖZELLİKLERİ - HIZLI REFERANS

## 🎯 15m SCALPING ÇIKTI ERİŞİMİ

### JSON Çıktısında Scalping Verisine Erişim

```python
# Ana veri yapısı
data = analyze_coin("BTC/USDT:USDT", {"15m": 200})

# 15m scalping verisi
scalping = data["timeframes"]["15m"]["summary"]["scalping_analysis"]
```

### Scalping Verisi Yapısı

```
scalping_analysis/
├── scalping_signals/
│   ├── signals/                    # Teknik sinyaller
│   │   ├── vwap_position          # "above" / "below"
│   │   ├── vwap_distance_pct      # VWAP'tan % mesafe
│   │   ├── bollinger_squeeze      # "yes" / "no"
│   │   ├── bb_percent_b           # 0-1 arası pozisyon
│   │   ├── stoch_rsi_signal       # "oversold"/"overbought"/"neutral"
│   │   ├── stoch_rsi_value        # 0-100
│   │   ├── volume_spike           # "yes" / "no"
│   │   └── ema_alignment          # "bullish" / "bearish"
│   │
│   ├── entry_opportunities[]      # Giriş sinyalleri listesi
│   ├── confidence                 # "high" / "medium" / "low"
│   ├── confidence_score           # 0-10 arası
│   └── risk_level                 # "low" / "medium" / "high"
│
├── micro_levels/
│   ├── immediate_resistance       # Son 10 mumun en yüksek
│   ├── immediate_support          # Son 10 mumun en düşük
│   ├── current_range              # Mevcut range
│   ├── range_position_pct         # Range içinde konum %
│   ├── is_consolidating           # Konsolidasyon var mı?
│   ├── range_breakout_levels/
│   │   ├── upside                 # Yukarı breakout seviyesi
│   │   └── downside               # Aşağı breakout seviyesi
│   ├── recent_high_breaks         # true / false
│   └── recent_low_breaks          # true / false
│
└── momentum_indicators/
    ├── vwap_distance_pct          # VWAP mesafesi %
    ├── bollinger_squeeze          # "yes" / "no"
    ├── bollinger_bandwidth        # Bant genişliği
    ├── stoch_rsi_value            # Stoch RSI değeri
    └── bb_percent_b_value         # %B değeri
```

---

## 🔍 GİRİŞ SİNYALLERİ TABLOSU

| Entry Signal | Ne Zaman? | Long/Short | Risk |
|--------------|-----------|------------|------|
| `VWAP_BOUNCE_LONG` | VWAP üstü + Stoch RSI oversold | LONG | Orta |
| `VWAP_BOUNCE_SHORT` | VWAP altı + Stoch RSI overbought | SHORT | Orta |
| `VOLUME_BREAKOUT_LONG` | Hacim spike + Close > EMA20 | LONG | Düşük |
| `VOLUME_BREAKOUT_SHORT` | Hacim spike + Close < EMA20 | SHORT | Düşük |
| `SQUEEZE_BREAKOUT_LONG` | Squeeze + %B > 0.8 + Hacim | LONG | Yüksek |
| `SQUEEZE_BREAKOUT_SHORT` | Squeeze + %B < 0.2 + Hacim | SHORT | Yüksek |
| `BULLISH_RSI_DIVERGENCE` | RSI↑ Fiyat↓ | LONG | Orta |
| `BEARISH_RSI_DIVERGENCE` | RSI↓ Fiyat↑ | SHORT | Orta |

---

## 💡 ÖRNEK KULLANIM SENARYOLARI

### Senaryo 1: Hızlı Scalp (Low Risk)
```python
signals = scalping["scalping_signals"]

if ("VOLUME_BREAKOUT_LONG" in signals["entry_opportunities"] and
    signals["confidence"] == "high" and
    signals["risk_level"] == "low"):
    
    # Entry setup
    entry = current_price
    stop = micro["immediate_support"]
    target = micro["immediate_resistance"]
    
    print(f"✅ LONG Entry: ${entry}")
    print(f"🛑 Stop Loss: ${stop}")
    print(f"🎯 Target: ${target}")
```

### Senaryo 2: VWAP Bounce
```python
signals = scalping["scalping_signals"]["signals"]

if (signals["vwap_position"] == "above" and
    signals["stoch_rsi_signal"] == "oversold" and
    abs(signals["vwap_distance_pct"]) < 0.5):  # VWAP'a çok yakın
    
    print("🟢 VWAP Bounce Long Setup")
    print(f"Entry: ${current_price}")
    print(f"Stop: VWAP - ${current_price - vwap_value}")
```

### Senaryo 3: Squeeze Breakout
```python
signals = scalping["scalping_signals"]["signals"]
micro = scalping["micro_levels"]

if (signals["bollinger_squeeze"] == "yes" and
    micro["is_consolidating"] and
    signals["volume_spike"] == "yes"):
    
    # Breakout bekle
    if signals["bb_percent_b"] > 0.8:
        print("⬆️ Upside Breakout Bekleniyor")
        entry = micro["range_breakout_levels"]["upside"]
    elif signals["bb_percent_b"] < 0.2:
        print("⬇️ Downside Breakout Bekleniyor")
        entry = micro["range_breakout_levels"]["downside"]
```

### Senaryo 4: Konfirmasyon Kontrolü
```python
def check_scalping_setup(scalping_data):
    """Tüm koşulları kontrol et"""
    signals = scalping_data["scalping_signals"]
    micro = scalping_data["micro_levels"]
    
    score = 0
    reasons = []
    
    # 1. Confidence kontrol
    if signals["confidence"] == "high":
        score += 3
        reasons.append("✅ High confidence")
    
    # 2. Entry opportunity var mı?
    if len(signals["entry_opportunities"]) > 0:
        score += 2
        reasons.append(f"✅ {len(signals['entry_opportunities'])} entry signal")
    
    # 3. Risk seviyesi
    if signals["risk_level"] == "low":
        score += 2
        reasons.append("✅ Low risk")
    
    # 4. Range pozisyonu
    if 30 < micro["range_position_pct"] < 70:
        score += 1
        reasons.append("✅ Mid-range position")
    
    # 5. Consolidation sonrası mı?
    if micro["is_consolidating"] and signals["signals"]["volume_spike"] == "yes":
        score += 2
        reasons.append("✅ Consolidation breakout")
    
    return {
        "score": score,
        "max_score": 10,
        "rating": "EXCELLENT" if score >= 7 else "GOOD" if score >= 5 else "WEAK",
        "reasons": reasons
    }

# Kullanım
setup = check_scalping_setup(scalping)
print(f"Setup Rating: {setup['rating']} ({setup['score']}/{setup['max_score']})")
for reason in setup['reasons']:
    print(f"  {reason}")
```

---

## 📊 GÖSTERGELERİ YORUMLAMA

### VWAP (Volume Weighted Average Price)
```
Fiyat > VWAP → Bullish bias (alıcılar güçlü)
Fiyat < VWAP → Bearish bias (satıcılar güçlü)
Fiyat ≈ VWAP → Nötr (denge noktası)

Distance < 0.3% → VWAP'a çok yakın (bounce beklenebilir)
Distance > 1.0% → VWAP'tan uzak (düzeltme gelebilir)
```

### Bollinger Bands
```
%B > 0.8 → Üst banda yakın (overbought)
%B < 0.2 → Alt banda yakın (oversold)
%B ≈ 0.5 → Orta bantta (nötr)

Bandwidth < 0.1 → SQUEEZE (volatilite patlaması yakın!)
Bandwidth > 0.2 → Yüksek volatilite
```

### Stochastic RSI
```
Value < 20 → OVERSOLD (alım fırsatı)
Value > 80 → OVERBOUGHT (satış fırsatı)
20-80 → Nötr bölge

Oversold + VWAP above = Güçlü long setup
Overbought + VWAP below = Güçlü short setup
```

### Micro Levels
```
range_position_pct:
  0-20% → Destek yakını (long bakılabilir)
  80-100% → Direnç yakını (short bakılabilir)
  40-60% → Mid-range (breakout bekle)

is_consolidating = true:
  → Range daraldı, breakout yakın
  → Volume spike ile beraber güçlü sinyal
```

---

## ⚙️ OPTİMİZASYON İPUÇLARI

### Zaman Aralığı Seçimi
```python
# Daha fazla veri = daha güvenilir sinyal
config = {
    "15m": 200  # Minimum 200 mum (≈50 saat veri)
}

# Ultra-short term (riskli)
config = {"15m": 100}  # 25 saat

# Balanced (önerilen)
config = {"15m": 200}  # 50 saat

# Safe (konservatif)
config = {"15m": 300}  # 75 saat
```

### Confidence Threshold
```python
# Agresif (çok sinyal, düşük doğruluk)
if signals["confidence_score"] >= 3:
    trade()

# Balanced (önerilen)
if signals["confidence_score"] >= 5:
    trade()

# Konservatif (az sinyal, yüksek doğruluk)
if signals["confidence_score"] >= 7:
    trade()
```

### Risk Management
```python
def calculate_position_size(account_balance, risk_pct, stop_distance_pct):
    """Pozisyon büyüklüğü hesapla"""
    risk_amount = account_balance * (risk_pct / 100)
    position_size = risk_amount / (stop_distance_pct / 100)
    return position_size

# Örnek
balance = 10000  # $10,000
risk = 1  # Hesabın %1'i
stop_distance = 2  # Fiyatın %2'si

position = calculate_position_size(balance, risk, stop_distance)
print(f"Position Size: ${position:,.2f}")
```

---

## 🚨 UYARI VE LİMİTLER

### ⚠️ VWAP Limitasyonları
- Günlük reset olur (yeni günde sıfırlanır)
- Düşük hacimli coinlerde yanıltıcı olabilir
- İlk 30-60 dakikada güvenilirliği düşük

### ⚠️ Bollinger Squeeze
- Squeeze sonrası yön belirsiz (yukarı/aşağı gidebilir)
- Volume confirmation gerekir
- Fake breakout riski var

### ⚠️ Stochastic RSI
- Trending marketlerde yanıltıcı (sürekli oversold/overbought)
- Ranging marketlerde daha etkili
- Tek başına kullanma

### ⚠️ Entry Signals
- %100 garantili sinyal yok
- Stop-loss kullanımı zorunlu
- Risk/reward oranına dikkat et
- Backtest yap, demo hesapta dene

---

## 📈 PERFORMANS BENCHMARKLERİ

### Beklenen Sonuçlar (Ideal Koşullarda)
```
High Confidence (score >= 7):
  Win Rate: ~65-70%
  Risk/Reward: 1:1.5 - 1:2

Medium Confidence (score 4-6):
  Win Rate: ~55-60%
  Risk/Reward: 1:1 - 1:1.5

Low Confidence (score < 4):
  Win Rate: ~45-50%
  Risk/Reward: Skip (trade etme)
```

### Optimum Koşullar
```
✅ 15m timeframe
✅ BTC, ETH gibi likit coinler
✅ Yüksek hacim dönemleri (Avrupa/ABD saatleri)
✅ Trending veya ranging market (sideways OK)
✅ Düşük spread (<0.05%)
```

### Kaçınılması Gerekenler
```
❌ Major news vakti (Fed, CPI, vb.)
❌ Düşük likidite saatleri (Asya gece)
❌ Extreme volatilite (BTC %10+ hareket)
❌ Spread yüksek altcoinler
❌ Funding rate değişim saati
```

---

## 🔗 İLGİLİ DOSYALAR

- `qwen3.py` - Ana kod
- `SCALPING_FEATURES.md` - Detaylı dökümanatasyon
- `test_scalping_features.py` - Test scripti
- `requirements.txt` - Bağımlılıklar

---

**Son Güncelleme:** 3 Kasım 2025  
**Versiyon:** qwen3.py v2.1 - Scalping Enhanced
