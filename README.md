# Bitcoin Technical Analysis Engine 📊

AI-ready Bitcoin (BTCUSDT) teknik analiz motoru. Binance Futures'dan canlı veri çeker, gelişmiş teknik analiz yapar ve Supabase'e kaydeder.

## 🚀 Özellikler

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

## 📋 Gereksinimler

- Python 3.8+
- Supabase hesabı
- İnternet bağlantısı (Binance API için)

## ⚙️ Kurulum

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/KULLANICI_ADINIZ/qwen3-analiz-py.git
cd qwen3-analiz-py
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

## 🎯 Kullanım

### Gelişmiş Analiz (Sadece Summary)
```bash
python qwen3.py
```

**Çıktı:** JSON formatında analiz özeti
**Supabase Tablosu:** `btc_analysis`

### Ham Veri (Tüm Mumlar)
```bash
python qwen3_AllData.py
```

**Çıktı:** JSON + `btc_data_multi_tf.json` dosyası
**Supabase Tablosu:** `btc_raw_data`

## 📊 Çıktı Formatı

```json
{
  "symbol": "BTC/USDT:USDT",
  "as_of_utc": "2025-11-03T12:00:00Z",
  "timeframes": {
    "4h": {
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

### Tablo: `btc_analysis`
- Analiz sonuçları (summary)
- Her çalıştırmada güncellenir
- JSONB formatında esnek veri yapısı

### Tablo: `btc_raw_data`
- Ham OHLCV verileri
- Her mum için detaylı indikatörler
- Grafik çizimi için kullanılabilir

## 🔄 Otomasyonlar

### Windows Task Scheduler
```powershell
# Her 4 saatte bir çalıştır
schtasks /create /tn "BTC Analysis" /tr "python C:\path\to\qwen3.py" /sc hourly /mo 4
```

### Linux Cron
```bash
# Her 4 saatte bir
0 */4 * * * /usr/bin/python3 /path/to/qwen3.py
```

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
