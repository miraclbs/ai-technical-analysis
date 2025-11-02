# Supabase Kurulum Rehberi

Bu kod, Bitcoin analiz verilerini Supabase veritabanına otomatik olarak kaydeder.

## 1. Supabase Projesi Oluşturma

1. [Supabase](https://supabase.com) sitesine gidin ve ücretsiz hesap açın
2. "New Project" butonuna tıklayın
3. Proje bilgilerinizi girin ve projeyi oluşturun

## 2. Veritabanı Tablosu Oluşturma

Supabase Dashboard'da **SQL Editor** bölümüne gidin ve şu SQL komutunu çalıştırın:

```sql
-- BTC analiz verileri için tablo
CREATE TABLE btc_analysis (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    as_of_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    timeframes JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hızlı sorgulama için index
CREATE INDEX idx_btc_analysis_as_of ON btc_analysis(as_of_utc DESC);
CREATE INDEX idx_btc_analysis_symbol ON btc_analysis(symbol);

-- RLS (Row Level Security) politikası - herkese okuma izni
ALTER TABLE btc_analysis ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON btc_analysis
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON btc_analysis
    FOR INSERT WITH CHECK (true);
```

## 3. API Anahtarlarını Alma

1. Supabase Dashboard'da **Settings** > **API** bölümüne gidin
2. Şu bilgileri kopyalayın:
   - **Project URL** (örnek: `https://xyzcompany.supabase.co`)
   - **anon public** veya **service_role** key

## 4. Çevre Değişkenlerini Ayarlama

### Windows (PowerShell):
```powershell
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_KEY="your-supabase-anon-or-service-key"
```

### Windows (Command Prompt):
```cmd
set SUPABASE_URL=https://your-project-id.supabase.co
set SUPABASE_KEY=your-supabase-anon-or-service-key
```

### Linux/Mac:
```bash
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_KEY="your-supabase-anon-or-service-key"
```

### Kalıcı Ayar (Önerilen):

`.env` dosyası oluşturun (`.env.example` dosyasını kopyalayın):

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
```

Ardından `python-dotenv` paketini yükleyin ve kodu güncelleyin:

```bash
pip install python-dotenv
```

`qwen3.py` dosyasının başına ekleyin:
```python
from dotenv import load_dotenv
load_dotenv()  # .env dosyasını yükle
```

## 5. Kodu Çalıştırma

```bash
python qwen3.py
```

Kod çalıştığında:
- Bitcoin analiz verilerini çeker
- JSON formatında konsola yazdırır
- Supabase veritabanına otomatik olarak kaydeder
- Başarılı kayıt mesajı gösterir

## 6. Verileri Görüntüleme

Supabase Dashboard'da **Table Editor** > **btc_analysis** tablosuna giderek kaydedilen verileri görebilirsiniz.

### SQL ile Sorgulama:

```sql
-- Son 10 analizi getir
SELECT * FROM btc_analysis 
ORDER BY as_of_utc DESC 
LIMIT 10;

-- Belirli bir tarih aralığındaki analizler
SELECT * FROM btc_analysis 
WHERE as_of_utc >= '2025-01-01'
ORDER BY as_of_utc DESC;

-- JSON içinden belirli bir veriyi çıkarma (örnek: 4h timeframe RSI)
SELECT 
    as_of_utc,
    timeframes->'4h'->'summary'->'indicators'->'rsi'->'value' as rsi_4h
FROM btc_analysis
ORDER BY as_of_utc DESC
LIMIT 10;
```

## Güvenlik Notları

- **Asla** API anahtarlarınızı GitHub'a yüklemeyin
- `.env` dosyasını `.gitignore`'a ekleyin
- Production ortamında `service_role` key yerine `anon` key kullanın
- RLS (Row Level Security) politikalarını ihtiyacınıza göre ayarlayın
