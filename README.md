# Türkiye Karbon Emisyon Analizi

Bu proje, Türkiye'deki fabrikaların karbon emisyonlarını analiz eden ve gelecek tahminleri sunan bir web uygulamasıdır.

## 🌟 Özellikler

- **📊 Tüm Türkiye Analizi**: 81 ildeki fabrikaların emisyon analizi
- **🔮 AI Destekli Tahminler**: 2025 yılı için emisyon tahminleri
- **📈 Gelecek Senaryoları**: Farklı ekonomik koşullarda emisyon senaryoları
- **🤖 AI Analizi**: GPT destekli sürdürülebilirlik önerileri

## 🚀 Canlı Demo

[Türkiye Karbon Emisyon Analizi]([https://turkiye-karbon-emisyon-analizi.vercel.app](https://turkey-carbon-emission-analysis.onrender.com)

## 💻 Teknolojiler

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **AI**: OpenAI GPT
- **Veri**: OpenStreetMap API, gerçek emisyon faktörleri
- **Deployment**: Vercel

## 📁 Proje Yapısı

```
├── src/                    # Python kaynak kodu
│   ├── web_app.py         # Ana Flask uygulaması
│   ├── factory_emissions.py
│   └── gpt_integration.py
├── templates/             # HTML şablonları
├── static/               # CSS, JS, veri dosyaları
├── api/                  # Vercel API endpoint'i
└── config/               # Yapılandırma dosyaları
```

## 🏃‍♂️ Yerel Çalıştırma

```bash
# Repository'yi klonlayın
git clone https://github.com/rumeysakara/turkiye-karbon-emisyon-analizi.git
cd turkiye-karbon-emisyon-analizi

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python src/web_app.py
```

Uygulama http://localhost:8080 adresinde çalışacaktır.

## 📊 Veri Kaynakları

- **Fabrika Verileri**: OpenStreetMap Overpass API
- **Emisyon Faktörleri**: IPCC Guidelines, IEA Energy Statistics, DEFRA
- **Büyüme Oranları**: TÜİK Sanayi Üretim İndeksi

## 🔧 Yapılandırma

AI özelliklerini kullanmak için `config/openai_config.json` dosyasını oluşturun:

```json
{
  "OPENAI_API_KEY": "your_api_key_here",
  "model": "gpt-4o-mini"
}
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👩‍💻 Geliştirici

**Rumeysa Kara** - [GitHub](https://github.com/rumeysakara)

---

🌱 **Sürdürülebilir bir gelecek için teknoloji**
