import streamlit as st
import anthropic
import random
from datetime import datetime, timedelta
import time as time_module

st.set_page_config(page_title="KOBİ Asistan", page_icon="🌿", layout="wide")

st.markdown("""
<style>
.stApp { background: #f7f7f3; }
.main .block-container { padding-top: 1rem; max-width: 1100px; }
.chat-user { background:#1D9E75; color:white; padding:10px 14px; border-radius:14px 14px 3px 14px; display:inline-block; max-width:80%; font-size:14px; line-height:1.5; margin:4px 0; }
.chat-bot  { background:white; color:#1a1a1a; border:1px solid #e8e8e2; padding:10px 14px; border-radius:14px 14px 14px 3px; display:inline-block; max-width:80%; font-size:14px; line-height:1.5; margin:4px 0; }
.row-user  { text-align:right; margin:6px 0; }
.row-bot   { text-align:left;  margin:6px 0; }
.tool-pill { background:#E1F5EE; color:#0F6E56; font-size:11px; padding:2px 8px; border-radius:8px; font-weight:600; display:inline-block; margin-bottom:4px; }
.report-card { background:#fafaf7; border:1px solid #e0e0da; border-radius:10px; padding:14px; font-size:13px; margin-top:6px; }
.rc-row { display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #f0f0ea; }
.rc-row:last-child { border-bottom:none; }
</style>
""", unsafe_allow_html=True)

NAMES  = ["Ahmet Yılmaz","Fatma Kaya","Mehmet Demir","Ayşe Çelik","Can Arslan","Zeynep Kurt","Ali Şahin","Elif Aydın","Murat Öztürk","Selin Çetin","Hasan Kılıç","Merve Doğan","Emre Yıldız","Büşra Aksoy","Tolga Güneş","Hatice Eren","Serkan Polat","Neslihan Koç","Burak Acar","Gizem Şen"]
PRODS  = ["Organik Domates 5kg","Zeytinyağı 1L","Bal 500g","Peynir 1kg","Zeytin 500g","Ceviz 1kg","Nohut 2kg","Organik Yumurta 15li","Tarhana 500g","Kekik 100g"]
SEHIR  = ["Ankara","İstanbul","İzmir","Bursa","Antalya","Konya","Adana","Gaziantep","Mersin","Trabzon"]
ANK_D  = ["Çankaya","Keçiören","Mamak","Altındağ","Yenimahalle","Etimesgut","Sincan","Pursaklar","Gölbaşı","Polatlı"]
IST_D  = ["Kadıköy","Beşiktaş","Şişli","Üsküdar","Fatih","Beyoğlu","Bakırköy","Maltepe","Ataşehir","Pendik"]
OTH_D  = ["Konya Selçuklu","İzmir Konak","Bursa Osmangazi","Adana Seyhan","Antalya Muratpaşa","Gaziantep Şahinbey","Mersin Yenişehir","Kayseri Melikgazi","Samsun Atakum","Trabzon Ortahisar","Diyarbakır Bağlar","Malatya Battalgazi","Denizli Pamukkale","Muğla Bodrum","Aydın Efeler"]

def pick(a): return a[int(random.random()*len(a))]

# SESSION STATE
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = []
if "report_sent" not in st.session_state:
    st.session_state.report_sent = False
if "pending_msg" not in st.session_state:
    st.session_state.pending_msg = None
if "kargolar" not in st.session_state:
    kargolar = []
    for i in range(12):
        s = ANK_D[i%len(ANK_D)] if i<3 else (IST_D[i%len(IST_D)] if i<6 else pick(SEHIR))
        d = "yolda" if i<4 else ("girildi" if i<7 else ("teslim edildi" if i<10 else "gecikiyor"))
        kargolar.append({"id":i,"kod":f"TRK{900000+128+i}","sipNo":128+i,"musteri":NAMES[i%len(NAMES)],"urun":pick(PRODS),"sehir":s,"durum":d,"tarih":datetime.now().strftime("%d.%m.%Y")})
    st.session_state.kargolar = kargolar
if "stok" not in st.session_state:
    st.session_state.stok = [
        {"name":"Organik Domates","unit":"kg","quantity":45,"threshold":50},
        {"name":"Zeytinyağı","unit":"litre","quantity":120,"threshold":20},
        {"name":"Bal","unit":"adet","quantity":18,"threshold":10},
        {"name":"Peynir","unit":"kg","quantity":8,"threshold":15},
        {"name":"Zeytin","unit":"kg","quantity":200,"threshold":30},
    ]
if "orders" not in st.session_state:
    orders = []
    for i in range(150):
        c = ANK_D[i%len(ANK_D)] if i<10 else (IST_D[(i-10)%len(IST_D)] if i<30 else ("—" if i<80 else pick(OTH_D)))
        s = "hazırlanıyor" if i<80 else pick(["kargoda","teslim edildi","gecikiyor","beklemede"])
        orders.append({"id":128+i,"musteri":NAMES[i%len(NAMES)],"urun":pick(PRODS),"status":s,"city":c})
    st.session_state.orders = orders

def stok_durum(q, t):
    if q <= t: return "Kritik 🔴"
    if q <= t*1.3: return "Düşük 🟡"
    return "Yeterli 🟢"

def build_prompt():
    K = st.session_state.kargolar
    S = st.session_state.stok
    yolda   = sum(1 for k in K if k["durum"]=="yolda")
    gec     = sum(1 for k in K if k["durum"]=="gecikiyor")
    teslim  = sum(1 for k in K if k["durum"]=="teslim edildi")
    girildi = sum(1 for k in K if k["durum"]=="girildi")
    kdet = "\n".join(f"#{k['sipNo']} {k['musteri']} → {k['sehir']} [{k['durum']}] {k['kod']}" for k in K)
    sozet = " | ".join(f"{s['name']}: {s['quantity']}{s['unit']} (eşik:{s['threshold']}, {stok_durum(s['quantity'],s['threshold'])})" for s in S)
    ank = sum(1 for o in st.session_state.orders if o["city"] in ANK_D)
    ist = sum(1 for o in st.session_state.orders if o["city"] in IST_D)
    haz = sum(1 for o in st.session_state.orders if o["status"]=="hazırlanıyor")
    return f"""Sen KOBİ Asistanısın. Türkçe, kısa ve net yanıtlar ver. Madde madde yaz.

SİPARİŞ (150 toplam): Ankara:{ank} | İstanbul:{ist} | Hazırlanıyor:{haz} | Diğer:{150-ank-ist-haz}

KARGO ({len(K)} toplam): Yolda:{yolda} | Teslim:{teslim} | Geciken:{gec} | Girildi:{girildi}
{kdet}

STOK: {sozet}

Kritik stok veya gecikme varsa sormadan uyar. Günlük rapor 21:00'de otomatik çıkar."""

def send_claude(text):
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "❌ API key ayarlanmamış."
    client = anthropic.Anthropic(api_key=api_key)
    # Sadece user/assistant mesajlarını gönder
    msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_msgs if m["role"] in ("user","assistant") and m.get("content") != "__REPORT__"]
    msgs.append({"role":"user","content":text})
    r = client.messages.create(model="claude-sonnet-4-5", max_tokens=800, system=build_prompt(), messages=msgs)
    return r.content[0].text

def tool_label(text):
    low = text.lower()
    if any(w in low for w in ["kargo","yolda","teslim","gecikim"]): return "🚚 check_cargo"
    if any(w in low for w in ["stok","kritik"]): return "📦 check_stock"
    if any(w in low for w in ["rapor","günlük","özet"]): return "📊 daily_report"
    if any(c.isdigit() for c in text) or "sipariş" in low: return "🔍 check_order"
    return None

def build_report():
    K = st.session_state.kargolar
    S = st.session_state.stok
    yolda   = [k for k in K if k["durum"]=="yolda"]
    teslim  = [k for k in K if k["durum"]=="teslim edildi"]
    geciken = [k for k in K if k["durum"]=="gecikiyor"]
    girildi = [k for k in K if k["durum"]=="girildi"]
    kritik  = [s for s in S if s["quantity"]<=s["threshold"]]
    tarih   = datetime.now().strftime("%d.%m.%Y")
    stok_rows = "".join(f'<div class="rc-row"><span>{s["name"]}</span><span>{s["quantity"]} {s["unit"]} — {stok_durum(s["quantity"],s["threshold"])}</span></div>' for s in S)
    yolda_rows = "".join(f'<div class="rc-row"><span>{k["musteri"]}</span><span style="color:#888;font-size:12px;">{k["kod"]} · {k["sehir"]}</span></div>' for k in yolda[:6])
    gec_rows = "".join(f'<div class="rc-row"><span>{k["musteri"]}</span><span style="color:#A32D2D;">{k["sehir"]}</span></div>' for k in geciken)
    kritik_w = f'<div style="background:#fff0f0;border:1px solid #f0c0c0;border-radius:7px;padding:8px;color:#A32D2D;font-size:12px;margin-top:8px;">⚠️ Kritik stok: {", ".join(s["name"] for s in kritik)}</div>' if kritik else ""
    return f"""
    <div class="report-card">
        <div style="font-weight:700;font-size:14px;margin-bottom:10px;">📈 Günlük rapor — {tarih} 21:00</div>
        <div style="font-size:11px;font-weight:700;color:#888;margin-bottom:5px;">🚚 KARGO ({len(K)} toplam)</div>
        <div class="rc-row"><span>Yolda</span><span style="color:#185FA5;font-weight:600;">{len(yolda)}</span></div>
        <div class="rc-row"><span>Teslim edildi</span><span style="color:#3B6D11;font-weight:600;">{len(teslim)}</span></div>
        <div class="rc-row"><span>Gecikiyor</span><span style="color:#A32D2D;font-weight:600;">{len(geciken)}</span></div>
        <div class="rc-row"><span>Girildi/bekliyor</span><span style="font-weight:600;">{len(girildi)}</span></div>
        {"<div style='font-size:11px;font-weight:700;color:#888;margin:8px 0 4px;'>Yoldaki kargolar</div>" + yolda_rows if yolda else ""}
        {"<div style='font-size:11px;font-weight:700;color:#A32D2D;margin:8px 0 4px;'>⚠️ Geciken</div>" + gec_rows if geciken else ""}
        <div style="font-size:11px;font-weight:700;color:#888;margin:8px 0 4px;">📦 STOK</div>
        {stok_rows}{kritik_w}
    </div>"""

# SIDEBAR
with st.sidebar:
    st.markdown("### 🌿 KOBİ Asistan")
    now = datetime.now()
    st.markdown(f"🕐 **{now.strftime('%H:%M')}**")
    target = now.replace(hour=21,minute=0,second=0,microsecond=0)
    if now >= target: target += timedelta(days=1)
    diff = int((target-now).total_seconds())
    h,r = divmod(diff,3600); m,s = divmod(r,60)
    st.markdown(f"📊 Sonraki rapor: **{h:02d}:{m:02d}:{s:02d}**")
    st.divider()
    K = st.session_state.kargolar
    c1,c2 = st.columns(2)
    c1.metric("Toplam Kargo", len(K))
    c2.metric("Yolda", sum(1 for k in K if k["durum"]=="yolda"))
    c1.metric("Geciken", sum(1 for k in K if k["durum"]=="gecikiyor"))
    c2.metric("Kritik Stok", sum(1 for s in st.session_state.stok if s["quantity"]<=s["threshold"]))
    if now.hour==21 and now.minute==0 and not st.session_state.report_sent:
        st.session_state.report_sent = True
        st.session_state.chat_msgs.append({"role":"assistant","content":"__REPORT__","report_html":build_report(),"tool":"📊 Günlük otomatik rapor"})

# SEKMELER
tab1, tab2, tab3 = st.tabs(["💬 Asistan", "🚚 Kargo Yönetimi", "📦 Stok Yönetimi"])

# ── CHAT ─────────────────────────────────────────────
with tab1:
    st.markdown("#### 💬 Müşteri Asistanı")

    # Hızlı sorular
    chips = ["Yoldaki kargolar?","Kritik stoklar?","Geciken var mı?","Günlük rapor","Ankara siparişleri?"]
    cols = st.columns(len(chips))
    for i,q in enumerate(chips):
        if cols[i].button(q, key=f"chip_{i}", use_container_width=True):
            st.session_state.pending_msg = q

    col_r = st.columns([5,1])
    with col_r[1]:
        if st.button("📊 Rapor test", use_container_width=True):
            st.session_state.chat_msgs.append({"role":"assistant","content":"__REPORT__","report_html":build_report(),"tool":"📊 Günlük otomatik rapor"})

    st.divider()

    # Mesaj göster
    chat_area = st.container(height=400)
    with chat_area:
        if not st.session_state.chat_msgs:
            st.markdown('<div class="row-bot"><div class="chat-bot">Merhaba! Sipariş, stok ve kargo konularında yardımcı olabilirim.<br>Her akşam <strong>21:00</strong>\'de günlük rapor otomatik olarak burada görünecek.</div></div>', unsafe_allow_html=True)
        for msg in st.session_state.chat_msgs:
            if msg["role"] == "user":
                st.markdown(f'<div class="row-user"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                tool = msg.get("tool","")
                tp = f'<div class="tool-pill">{tool}</div><br>' if tool else ""
                if msg.get("content") == "__REPORT__":
                    st.markdown(f'<div class="row-bot"><div class="chat-bot">{tp}{msg.get("report_html","")}</div></div>', unsafe_allow_html=True)
                else:
                    c = msg["content"].replace("\n","<br>")
                    st.markdown(f'<div class="row-bot"><div class="chat-bot">{tp}{c}</div></div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Mesaj yazın...")

    # pending_msg varsa onu kullan
    if st.session_state.pending_msg:
        user_input = st.session_state.pending_msg
        st.session_state.pending_msg = None

    if user_input:
        st.session_state.chat_msgs.append({"role":"user","content":user_input})
        with st.spinner("Yanıt hazırlanıyor..."):
            try:
                reply = send_claude(user_input)
                tl = tool_label(user_input)
                st.session_state.chat_msgs.append({"role":"assistant","content":reply,"tool":tl})
            except Exception as e:
                st.session_state.chat_msgs.append({"role":"assistant","content":f"❌ Hata: {e}"})
        st.rerun()

# ── KARGO ─────────────────────────────────────────────
with tab2:
    st.markdown("#### 🚚 Kargo Yönetimi")
    with st.expander("➕ Yeni kargo girişi", expanded=True):
        c1,c2,c3 = st.columns(3)
        k_kod = c1.text_input("Takip kodu", placeholder="TRK123456")
        k_mus = c2.text_input("Müşteri adı", placeholder="Ad Soyad")
        k_sip = c3.number_input("Sipariş no", min_value=1, value=200, step=1)
        c4,c5,c6 = st.columns(3)
        k_urun = c4.text_input("Ürün", placeholder="Organik Domates 5kg")
        k_seh  = c5.text_input("Şehir", placeholder="Ankara")
        k_dur  = c6.selectbox("Durum", ["girildi","yolda","teslim edildi","gecikiyor"])
        if st.button("🚚 Kargo Ekle", type="primary"):
            if k_kod and k_mus:
                st.session_state.kargolar.insert(0,{"id":int(time_module.time()*1000),"kod":k_kod,"sipNo":int(k_sip),"musteri":k_mus,"urun":k_urun or pick(PRODS),"sehir":k_seh or pick(SEHIR),"durum":k_dur,"tarih":datetime.now().strftime("%d.%m.%Y")})
                st.success(f"✓ '{k_kod}' eklendi")
                st.rerun()
            else:
                st.warning("Takip kodu ve müşteri adı zorunlu")

    st.divider()
    st.markdown("**Kargo listesi**")
    DUR_OPT = ["girildi","yolda","teslim edildi","gecikiyor"]
    DUR_EMO = {"girildi":"⬜ Girildi","yolda":"🔵 Yolda","teslim edildi":"🟢 Teslim edildi","gecikiyor":"🔴 Gecikiyor"}
    to_del = []
    for idx,k in enumerate(st.session_state.kargolar):
        cols = st.columns([2,1.5,2,1.5,2,0.5])
        cols[0].markdown(f"`{k['kod']}`")
        cols[1].markdown(f"#{k['sipNo']}")
        cols[2].markdown(k["musteri"])
        cols[3].markdown(k["sehir"])
        nd = cols[4].selectbox("",DUR_OPT,index=DUR_OPT.index(k["durum"]),format_func=lambda x:DUR_EMO[x],key=f"kd_{k['id']}",label_visibility="collapsed")
        if nd != k["durum"]:
            st.session_state.kargolar[idx]["durum"] = nd
            st.rerun()
        if cols[5].button("✕",key=f"kdel_{k['id']}"):
            to_del.append(k["id"])
    if to_del:
        st.session_state.kargolar = [k for k in st.session_state.kargolar if k["id"] not in to_del]
        st.rerun()

# ── STOK ──────────────────────────────────────────────
with tab3:
    st.markdown("#### 📦 Stok Yönetimi")
    st.markdown("**Mevcut stoklar**")
    sdel = []
    changed = False
    for idx,s in enumerate(st.session_state.stok):
        d = stok_durum(s["quantity"],s["threshold"])
        cols = st.columns([2.5,1.5,1,1,1.5,0.5])
        cols[0].markdown(f"**{s['name']}**")
        nq = cols[1].number_input("",min_value=0,value=s["quantity"],key=f"sq_{idx}",label_visibility="collapsed")
        cols[2].markdown(f"<span style='color:#888;font-size:13px;'>{s['unit']}</span>",unsafe_allow_html=True)
        cols[3].markdown(f"<span style='color:#888;font-size:13px;'>eşik:{s['threshold']}</span>",unsafe_allow_html=True)
        cols[4].markdown(d)
        if cols[5].button("✕",key=f"sdel_{idx}"): sdel.append(idx)
        if nq != s["quantity"]:
            st.session_state.stok[idx]["quantity"] = nq
            changed = True
    if sdel:
        st.session_state.stok = [s for i,s in enumerate(st.session_state.stok) if i not in sdel]
        st.rerun()
    if st.button("💾 Değişiklikleri kaydet", type="primary"):
        kritikler = [s["name"] for s in st.session_state.stok if s["quantity"]<=s["threshold"]]
        if kritikler: st.warning(f"⚠️ Kritik: {', '.join(kritikler)}")
        else: st.success("✓ Stok güncellendi")
    st.divider()
    with st.expander("➕ Yeni ürün ekle"):
        c1,c2,c3,c4 = st.columns(4)
        sn = c1.text_input("Ürün adı", placeholder="Organik Elma")
        su = c2.text_input("Birim", placeholder="kg")
        sq = c3.number_input("Miktar", min_value=0, value=0)
        st_ = c4.number_input("Eşik", min_value=0, value=0)
        if st.button("+ Ekle", type="primary"):
            if sn and su:
                st.session_state.stok.append({"name":sn,"unit":su,"quantity":int(sq),"threshold":int(st_)})
                st.success(f"✓ '{sn}' eklendi")
                st.rerun()
            else:
                st.warning("Ad ve birim zorunlu")
