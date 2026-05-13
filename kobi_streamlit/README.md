# 🌿 KOBİ Asistan
### Yapay Zeka Destekli KOBİ Operasyon Sistemi

> Küçük ve orta ölçekli işletmelerin sipariş, stok ve kargo süreçlerini yapay zeka ile otomatikleştiren,
> insan müdahalesini minimuma indiren akıllı bir asistan sistemi.

**🔗 Canlı Demo:** [kobi-asistan-crtsfpharkq8e2amxmtwgm.streamlit.app](https://kobi-asistan-crtsfpharkq8e2amxmtwgm.streamlit.app)

---

## 🎯 Problem

KOBİ'ler ve üretici kooperatifleri günlük operasyonlarını büyük ölçüde manuel yöntemlerle yürütmektedir:

- Müşteri talepleri e-posta, telefon veya mesajlaşma uygulamalarından karşılanmakta
- Sipariş ve stok takibi dağınık tablolara ya da kağıt bazlı sistemlere dayanmakta
- Kargo süreçleri elle kontrol edilmekte
- Bir işletme sahibi günde ortalama **2-3 saatini** yalnızca rutin soruları yanıtlamakla geçirmekte

Bu yapı; operasyonel verimsizliğe, insan kaynaklı hatalara, tutarsız müşteri deneyimine ve ölçeklenme güçlüklerine yol açmaktadır.

---

## 💡 Çözüm

KOBİ Asistan, bu süreçleri yapay zeka ile otomatikleştiren **3 modüllü entegre bir sistem**dir.

---

## 🖥️ Özellikler

### 💬 Müşteri Asistanı (AI Chatbot)
Doğal dil ile konuşabilen, işletmenin tüm verisine anlık erişimi olan bir yapay zeka asistanı.

- Sipariş durumu, kargo takibi ve stok sorularını saniyeler içinde yanıtlar
- Kritik durumlarda (geciken kargo, düşük stok) **sormadan proaktif uyarı** verir
- Her konuşmada sistemin güncel verisini kullanır — hiçbir bilgi eskimez

**Örnek konuşmalar:**
```
Kullanıcı: "128 numaralı siparişim nerede?"
Asistan:   "Sipariş #128 şu an kargoda. TRK900128 takip koduyla
            Ankara Çankaya'ya yönlendirilmiş."

Kullanıcı: "Domates stoğu ne kadar kaldı?"
Asistan:   "⚠️ Organik Domates stoku KRİTİK seviyede!
            45 kg mevcut, eşik değeri 50 kg.
            Acil sipariş verilmesi önerilir."
```

---

### 🚚 Kargo Yönetimi
Tüm kargo sürecini tek ekranda yönetebileceğiniz kontrol paneli.

- Yeni kargo girişi: takip kodu, müşteri adı, şehir ve ürün bilgisi
- Tek tıkla durum güncelleme:
```
⬜ Girildi  →  🔵 Yolda  →  🟢 Teslim Edildi
                          →  🔴 Gecikiyor
```
- Tüm durum değişiklikleri anında chatbota yansır
- Her akşam 21:00 raporuna otomatik olarak dahil edilir

---

### 📦 Stok Yönetimi
Anlık stok takibi ve kritik eşik uyarı sistemi.

- Tüm ürünlerin mevcut stok durumu tek ekranda
- Kritik eşik altına düşen ürünler anında 🔴 olarak işaretlenir
- Yeni ürün ekleme, miktar güncelleme, ürün silme
- Yapılan her değişiklik chatbot tarafından anında öğrenilir

---

### 📊 Günlük Otomatik Rapor
Her gün saat **21:00'de** otomatik olarak chatbota düşen özet rapor.

Rapor şunları içerir:
- Yoldaki kargolar ve takip kodları
- Geciken sevkiyatlar ve şehir bilgisi
- Tüm ürünlerin stok durumu
- Kritik stok uyarıları

> "Rapor test et" butonu ile istenildiğinde de tetiklenebilir.

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────┐
│         Kullanıcı (Tarayıcı)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Streamlit Frontend          │
│  ┌─────────┐ ┌────────┐ ┌────────┐ │
│  │ Chatbot │ │ Kargo  │ │  Stok  │ │
│  │ Sayfası │ │Yönetimi│ │Yönetimi│ │
│  └────┬────┘ └───┬────┘ └───┬────┘ │
│       └──────────┼──────────┘       │
│          Paylaşılan Veri Katmanı    │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        Anthropic Claude API         │
│         claude-sonnet-4-5           │
│                                     │
│  • Dinamik sistem promptu           │
│  • Güncel stok + kargo context      │
│  • Proaktif uyarı mantığı           │
└─────────────────────────────────────┘
```

---

## 🤖 Yapay Zeka Yaklaşımı

### Agent Mimarisi
Chatbot, her mesaj gönderildiğinde sistemdeki tüm güncel veriyi (kargo durumları, stok miktarları, sipariş bilgileri) otomatik olarak sistem promptuna ekler. Bu sayede AI her zaman en güncel bilgiyle yanıt verir.

### Proaktif Uyarı Sistemi
Kullanıcı sormadan bile kritik durumlar tespit edilir ve bildirilir:
- Stok eşik değerinin altına düşen ürünler
- Geciken kargo teslimatları

### Tool Routing
Kullanıcının mesajına göre hangi araç çalıştığı otomatik tespit edilir:

| Mesaj İçeriği | Araç |
|---------------|------|
| "kargo", "yolda", "teslim" | 🚚 check_cargo |
| "stok", "kritik" | 📦 check_stock |
| "rapor", "özet" | 📊 daily_report |
| Sipariş numarası | 🔍 check_order |

---

## 📊 Demo Veritabanı

| Veri | Detay |
|------|-------|
| Toplam sipariş | 150 |
| Ankara bölgesi | İlk 10 sipariş |
| İstanbul bölgesi | 11-30. siparişler |
| Hazırlanıyor | 31-80. siparişler |
| Türkiye geneli | 81-150. siparişler (70+ farklı ilçe) |
| Aktif kargo | 12 |
| Stok ürünleri | 5 kategori |

---

## 🚀 Kurulum

```bash
# Repoyu klonla
git clone https://github.com/zeynepsalkaya7/kobi-asistan.git
cd kobi-asistan/kobi_streamlit

# Bağımlılıkları yükle
pip install -r requirements.txt

# API key ayarla
mkdir .streamlit
echo 'ANTHROPIC_API_KEY = "sk-ant-..."' > .streamlit/secrets.toml

# Başlat
streamlit run app.py
```

> Anthropic API key: [console.anthropic.com](https://console.anthropic.com)

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| AI Model | Claude Sonnet 4.5 (Anthropic) |
| Frontend & Backend | Python / Streamlit |
| Deployment | Streamlit Cloud |
| API Güvenliği | st.secrets |

---

## 👤 Geliştirici

**Ümmühan Zeynep Salkaya**
[github.com/zeynepsalkaya7](https://github.com/zeynepsalkaya7)

> Tüm sistem — frontend, backend, AI entegrasyonu, deployment — tek başıma geliştirilmiştir.
