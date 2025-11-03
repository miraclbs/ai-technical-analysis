# Multi-Coin Technical Analysis Engine 📊

AI-ready çoklu kripto para teknik analiz motoru. Binance Futures'dan **BTC, ETH, SOL, BNB, XRP** için canlı veri çeker, gelişmiş teknik analiz yapar ve her coin için ayrı Supabase tablosuna kaydeder.

## 🚀 Özellikler

### Çoklu Coin Analizi
- 🎯 **Sabit 5 Coin:** BTC, ETH, SOL, BNB, XRP (her seferinde aynı coinler)
- 📊 **Ayrı Kayıt:** Her coin için ayrı tablo (btc_analysis, eth_analysis, vb.)
- ⚡ **Sıralı İşlem:** Tüm coinler sırayla analiz edilir

### Çoklu Timeframe Analizi
- **4h:** 100 mum analizi (~16 gün)
- **1h:** 150 mum analizi (~6 gün)
- **15m:** 200 mum analizi (~2 gün)

### Teknik İndikatörler
- ✅ RSI (Relative Strength Index)
- ✅ MACD (Moving Average Convergence Divergence)
- ✅ SMA/EMA (50, 100, 200 period)
- ✅ ATR (Average True Range)
- ✅ OBV (On-Balance Volume)
- ✅ Fibonacci Retracement Levels

### Gelişmiş Analizler
- 📈 **Trend Analizi:** Kısa/orta/uzun vadeli trend gücü
- 🎯 **Support/Resistance:** ATR bazlı dinamik seviyeler
- 📊 **Price Action:** Higher Highs/Lows, market structure
- 💹 **Volume Profili:** Hacim analizi ve bias tespiti
- ⚡ **MA Çaprazları:** Golden Cross / Death Cross
- 🕯️ **Mum Desenleri:** Doji, Hammer, Shooting Star, Morning/Evening Star

### Piyasa Bilgileri
- 💰 **Funding Rate:** Anlık fonlama oranı
- 📉 **Spread:** Bid/Ask farkı ve yüzdesi
- 💵 **Komisyonlar:** Maker/Taker ücretleri
- 📊 **24s Hacim:** Günlük işlem hacmi

## 📋 Gereksinimler

- Python 3.8+
- Supabase hesabı (her coin için ayrı tablo)
- İnternet bağlantısı (Binance API için)

## ⚙️ Kurulum

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/miraclbs/ai-technical-analysis.git
cd ai-technical-analysis
```

### 2. Virtual Environment Oluşturun (Opsiyonel)
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Supabase Kurulumu
`.env` dosyası oluşturun:
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 5. Veritabanı Tablolarını Oluşturun
Detaylı talimatlar için [`SUPABASE_SETUP.md`](SUPABASE_SETUP.md) dosyasına bakın.

**Not:** Her coin için ayrı tablo oluşturulur:
- `btc_analysis` - Bitcoin analizi
- `eth_analysis` - Ethereum analizi  
- `sol_analysis` - Solana analizi
- `bnb_analysis` - Binance Coin analizi
- (Diğer coinler için benzer şekilde)

## 🎯 Kullanım

### Çoklu Coin Analizi (Ana Script)
```bash
python qwen3.py
```

**İşlem Akışı:**
1. � Sabit coin listesi kullanılır (BTC, ETH, SOL, BNB, XRP)
2. 📊 Her coin için 3 timeframe'de (4h, 1h, 15m) analiz yapar
3. 💾 Her coin'in verisini ayrı tabloya kaydeder (örn: btc_analysis, eth_analysis)

**Çıktı:** 
- Console'da detaylı analiz özeti
- Her coin için ayrı Supabase tablosu

### Ham Veri (Tüm Mumlar - Sadece BTC)
```bash
python qwen3_AllData.py
```

**İşlem Akışı:**
- 4h: 100 mum analizi (~16.7 gün)
- 1h: 150 mum analizi (~6.25 gün)
- 15m: 200 mum analizi (~2.08 gün)

**Çıktı:** JSON + `btc_data_multi_tf.json` dosyası
**Supabase Tablosu:** `btc_raw_data`

## 📊 Çıktı Formatı

### Ana Analiz (qwen3.py)
```json
{
  "symbol": "BTC/USDT:USDT",
  "as_of_utc": "2025-11-03T12:00:00Z",
  "market_info": {
    "current_price": 86234.5,
    "volume_24h": 25847639221,
    "funding_rate": 0.0075,
    "spread_percentage": 0.012
  },
  "timeframes": {
    "4h": {
      "last_candle": {
        "timestamp": "2025-11-03T12:00:00Z",
        "open": 86100,
        "high": 86500,
        "low": 85900,
        "close": 86234.5,
        "volume": 1234567,
        "minutes_to_close": 45.2
      },
      "summary": {
        "key_levels": {
          "strong_support": [85000, 84500],
          "strong_resistance": [87000, 87500]
        },
        "indicators": {
          "rsi": {"value": 65.5, "trend": "rising"},
          "macd": {"histogram_trend": "rising", "crossover": "bullish"}
        },
        "trend_analysis": {
          "overall_direction": "bullish",
          "short_term": {"direction": "bullish", "strength_pct": 2.5}
        },
        "fibonacci": {
          "fib_0.618": 85420,
          "fib_0.5": 85900
        },
        "price_action": {
          "market_structure": "strong_uptrend"
        },
        "moving_averages": {
          "golden_cross": false,
          "ma_alignment": "bullish"
        }
      }
    },
    "1h": { "summary": {...} },
    "15m": { "summary": {...} }
  }
}
```

## 🗄️ Veritabanı Yapısı

### Dinamik Tablolar (Her Coin İçin Ayrı)
Her coin için otomatik olarak ayrı tablo oluşturulur:
- **`btc_analysis`** - Bitcoin analiz sonuçları
- **`eth_analysis`** - Ethereum analiz sonuçları
- **`sol_analysis`** - Solana analiz sonuçları
- **`bnb_analysis`** - Binance Coin analiz sonuçları
- **`xrp_analysis`** - Ripple analiz sonuçları

### Tablo Özellikleri
- ✅ Her çalıştırmada güncellenir (önceki veri silinir)
- ✅ JSONB formatında esnek veri yapısı
- ✅ Timestamp ile zaman damgası
- ✅ Market bilgileri (fiyat, hacim, funding rate)
- ✅ Timeframe bazlı detaylı analiz

### Ham Veri Tablosu
**Tablo:** `btc_raw_data` (sadece qwen3_AllData.py için)
- Ham OHLCV verileri
- Her mum için detaylı indikatörler
- Grafik çizimi için kullanılabilir

## 🔄 Otomasyonlar

### GitHub Actions (Önerilen - Bulut Tabanlı)
Repository'de otomatik çalışan GitHub Actions mevcut:
- ⏰ **Her 20 dakikada** bir otomatik analiz
- ☁️ Sunucu gerektirmez, tamamen ücretsiz
- 📊 Tüm coinler sırayla analiz edilir
- 💾 Supabase'e otomatik kayıt

GitHub Actions dosyası: `.github/workflows/analysis.yml`

### Windows Task Scheduler
```powershell
# Her 20 dakikada bir çalıştır
schtasks /create /tn "Crypto Analysis" /tr "python C:\path\to\qwen3.py" /sc minute /mo 20
```

### Linux Cron
```bash
# Her 20 dakikada bir
*/20 * * * * /usr/bin/python3 /path/to/qwen3.py
```

## 📈 Analiz Edilen Coinler

Script **her zaman sabit 5 coini** analiz eder:

**Analiz edilen coinler:**
1. 🟠 **BTC** (Bitcoin) - btc_analysis
2. 🔵 **ETH** (Ethereum) - eth_analysis
3. 🟣 **SOL** (Solana) - sol_analysis
4. 🟡 **BNB** (Binance Coin) - bnb_analysis
5. 🔴 **XRP** (Ripple) - xrp_analysis

**Not:** Bu liste sabittir ve her çalıştırmada aynı coinler analiz edilir.

## 🛡️ Güvenlik

- ⚠️ `.env` dosyasını asla GitHub'a yüklemeyin
- ⚠️ API anahtarlarınızı kimseyle paylaşmayın
- ✅ `.gitignore` dosyası `.env` dosyasını zaten hariç tutuyor

## 📚 Dökümantasyon

- [`SUPABASE_SETUP.md`](SUPABASE_SETUP.md) - Detaylı Supabase kurulum rehberi

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir! Büyük değişiklikler için lütfen önce bir issue açın.

## 📄 Lisans

MIT License

## 📧 İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.

---

**Not:** Bu proje eğitim amaçlıdır. Finansal tavsiye niteliği taşımaz. Yatırım kararlarınızı kendi araştırmanıza dayanarak verin.
