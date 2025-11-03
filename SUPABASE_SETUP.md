# Supabase Kurulum Rehberi

Bu kod, çoklu kripto para analiz verilerini Supabase veritabanına otomatik olarak kaydeder. Her coin için ayrı tablo oluşturulur.

## 1. Supabase Projesi Oluşturma

1. [Supabase](https://supabase.com) sitesine gidin ve ücretsiz hesap açın
2. "New Project" butonuna tıklayın
3. Proje bilgilerinizi girin ve projeyi oluşturun

## 2. Veritabanı Tablolarını Oluşturma

Supabase Dashboard'da **SQL Editor** bölümüne gidin ve şu SQL komutlarını çalıştırın:

### Opsiyon 1: Otomatik Tablo Oluşturma Fonksiyonu (ÖNERİLEN)

Bu fonksiyon, yeni coinler için otomatik olarak tablo oluşturur:

```sql
-- Dinamik tablo oluşturma fonksiyonu
CREATE OR REPLACE FUNCTION create_coin_analysis_table(coin_name TEXT)
RETURNS void AS $$
DECLARE
    table_name TEXT := coin_name || '_analysis';
BEGIN
    -- Tablo yoksa oluştur
    IF NOT EXISTS (
        SELECT FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = table_name
    ) THEN
        EXECUTE format('
            CREATE TABLE %I (
                id BIGSERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                as_of_utc TIMESTAMP WITH TIME ZONE NOT NULL,
                market_info JSONB,
                timeframes JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX idx_%I_as_of ON %I(as_of_utc DESC);
            CREATE INDEX idx_%I_symbol ON %I(symbol);
            
            ALTER TABLE %I ENABLE ROW LEVEL SECURITY;
            
            CREATE POLICY "Enable read access for all users" ON %I
                FOR SELECT USING (true);
            
            CREATE POLICY "Enable insert for authenticated users only" ON %I
                FOR INSERT WITH CHECK (true);
        ', table_name, table_name, table_name, table_name, table_name, table_name, table_name, table_name);
        
        RAISE NOTICE 'Tablo % oluşturuldu', table_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Popüler coinler için tabloları oluştur
SELECT create_coin_analysis_table('btc');
SELECT create_coin_analysis_table('eth');
SELECT create_coin_analysis_table('sol');
SELECT create_coin_analysis_table('bnb');
SELECT create_coin_analysis_table('xrp');
```

### Opsiyon 2: Manuel Tablo Oluşturma

Her coin için ayrı ayrı tablo oluşturmak isterseniz:

```sql
-- BTC analiz tablosu
CREATE TABLE btc_analysis (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    as_of_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    market_info JSONB,
    timeframes JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_btc_analysis_as_of ON btc_analysis(as_of_utc DESC);
CREATE INDEX idx_btc_analysis_symbol ON btc_analysis(symbol);

ALTER TABLE btc_analysis ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON btc_analysis
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON btc_analysis
    FOR INSERT WITH CHECK (true);

-- ETH, SOL, BNB, XRP için aynı yapıyı tekrarlayın
-- (btc_analysis yerine eth_analysis, sol_analysis, vb. kullanın)
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
