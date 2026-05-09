# 🌿 KOBİ Asistan

KOBİ'ler ve kooperatifler için yapay zeka destekli operasyon asistanı.

## Özellikler

- 💬 **AI Chatbot** — Sipariş, stok ve kargo sorularını doğal dille yanıtlar
- 🚚 **Kargo Yönetimi** — Kargo girişi ve durum takibi (Girildi → Yolda → Teslim)
- 📦 **Stok Yönetimi** — Kritik eşik uyarıları, ürün ekleme/güncelleme
- 📊 **Günlük Rapor** — Her akşam 21:00'de otomatik özet raporu

## Canlı Demo

👉 [kobi-asistan.streamlit.app](https://kobi-asistan.streamlit.app)

## Kurulum

```bash
pip install -r requirements.txt
streamlit run app.py
```

## AI Yaklaşımı

- Claude Sonnet modeli üzerinde agent mimarisi
- Her mesajda güncel stok ve kargo verisi dinamik olarak prompt'a eklenir
- Proaktif uyarı sistemi — kritik stok veya geciken kargo varsa kendiliğinden bildirir
- Günlük rapor otomasyonu — 21:00'de otomatik özet

## Mimari

```
Streamlit Frontend
      ↓
Anthropic Claude API (st.secrets ile güvenli key yönetimi)
      ↓
Mock veritabanı (sipariş, stok, kargo)
```

## Hedef Kitle

- 20-200 ürün yelpazesiyle çalışan e-ticaret işletmeleri
- Günde 10-100 sipariş işleyen butik firmalar  
- Tarım, gıda veya el sanatları kooperatifleri
