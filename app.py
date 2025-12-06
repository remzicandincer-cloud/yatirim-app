import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

# =========================
# SOL PANEL – PARAMETRELER
# =========================
st.sidebar.header(" Parametreler")

baslangic = st.sidebar.number_input("Başlangıç Tutarı (TL)", 0, 1_000_000, 6000)
ay_sayisi = st.sidebar.number_input("Yatırım Süresi (Ay)", 1, 240, 60)

st.sidebar.markdown("###  Aylık Getiri (%)")
iyi_oran = st.sidebar.number_input("En İyi", -10.0, 20.0, 3.0) / 100
orta_oran = st.sidebar.number_input("Ortalama", -10.0, 20.0, 1.2) / 100
kotu_oran = st.sidebar.number_input("Kötü", -10.0, 20.0, -0.5) / 100

# =========================
# MAVİ KISIM: AY ARALIKLARINDA EK YATIRIM
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader(" Ay Aralıklarında Ek Yatırım")

# Dinamik ek yatırım alanları
ek_yatirimlar = []
ek_yatirim_sayisi = st.sidebar.number_input("Kaç farklı ay aralığı için ek yatırım tanımlamak istiyorsunuz?", 
                                            min_value=0, max_value=10, value=4)

for i in range(ek_yatirim_sayisi):
    st.sidebar.markdown(f"**Aralık {i+1}**")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        baslangic_ay = st.sidebar.number_input(f"Başlangıç Ayı", min_value=1, max_value=240, value=(i*12)+1, key=f"bas_{i}")
    with col2:
        bitis_ay = st.sidebar.number_input(f"Bitiş Ayı", min_value=1, max_value=240, value=min(ay_sayisi, (i+1)*12), key=f"bit_{i}")
    with col3:
        ek_tutar = st.sidebar.number_input(f"Ek Tutar (TL)", min_value=0, max_value=100000, value=(i+1)*3000, key=f"tutar_{i}")
    
    if baslangic_ay <= bitis_ay:
        ek_yatirimlar.append({
            "baslangic": baslangic_ay,
            "bitis": bitis_ay,
            "tutar": ek_tutar
        })

# Varsayılan aylık ek yatırım
aylik_ek_varsayilan = st.sidebar.number_input("Varsayılan Aylık Ek Yatırım (TL)", 0, 100_000, 6000)

# =========================
# HESAPLAMA FONKSİYONU
# =========================
def hesapla(getiri):
    toplam = baslangic
    liste = []
    yatirilan = baslangic
    kar = 0
    
    for ay in range(1, ay_sayisi + 1):
        # Bu ay için ek yatırım tutarını belirle
        aylik_ek_aktif = aylik_ek_varsayilan
        
        # Ek yatırım aralıklarını kontrol et
        for ek in ek_yatirimlar:
            if ek["baslangic"] <= ay <= ek["bitis"]:
                aylik_ek_aktif = ek["tutar"]
                break
        
        # Getiri uygula
        toplam *= (1 + getiri)
        toplam += aylik_ek_aktif
        yatirilan += aylik_ek_aktif
        kar = toplam - yatirilan
        
        liste.append({
            "Ay": ay,
            "Toplam Birikim": round(toplam, 2),
            "Toplam Yatırılan": yatirilan,
            "Kar/Zarar": round(kar, 2),
            "Aylık Ek Yatırım": aylik_ek_aktif
        })
    
    return pd.DataFrame(liste)

df_iyi = hesapla(iyi_oran)
df_orta = hesapla(orta_oran)
df_kotu = hesapla(kotu_oran)

# =========================
# ANA LAYOUT
# =========================
col1, col2 = st.columns([1.1, 2.4])

# =========================
# SOL - TABLO
# =========================
with col1:
    st.subheader(" Aylık Yatırım Tablosu")
    st.dataframe(
        df_orta[["Ay", "Aylık Ek Yatırım", "Toplam Yatırılan", "Toplam Birikim", "Kar/Zarar"]],
        height=500,
        use_container_width=True
    )

# =========================
# SAĞ - YATIRIM AKIŞI VE ALTINDA 3 GRAFİK
# =========================
with col2:
    # ÜSTTE: YATIRIM AKIŞI GRAFİĞİ
    st.subheader(" Yatırım Akışı")
    
    fig_flow = go.Figure()
    
    fig_flow.add_trace(go.Scatter(
        x=df_kotu["Ay"],
        y=df_kotu["Toplam Birikim"],
        mode='lines',
        name="Kötü Senaryo",
        line=dict(color='rgba(239, 83, 80, 0.9)', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(239, 83, 80, 0.08)'
    ))
    
    fig_flow.add_trace(go.Scatter(
        x=df_orta["Ay"],
        y=df_orta["Toplam Birikim"],
        mode='lines',
        name="Ortalama Senaryo",
        line=dict(color='rgba(255, 167, 38, 0.9)', width=2.5),
        fill='tonexty',
        fillcolor='rgba(255, 167, 38, 0.08)'
    ))
    
    fig_flow.add_trace(go.Scatter(
        x=df_iyi["Ay"],
        y=df_iyi["Toplam Birikim"],
        mode='lines',
        name="En İyi Senaryo",
        line=dict(color='rgba(102, 187, 106, 0.9)', width=2.5),
        fill='tonexty',
        fillcolor='rgba(102, 187, 106, 0.08)'
    ))
    
    fig_flow.update_layout(
        height=300,
        xaxis_title="Ay",
        yaxis_title="Toplam Birikim (TL)",
        hovermode='x unified',
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.7)',
            font=dict(size=12)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        margin=dict(t=30, b=10)
    )
    
    st.plotly_chart(fig_flow, use_container_width=True)
    
    # ALTTA: 3 BÜYÜK GRAFİK (ESKİ BOYUTUNDA)
    st.markdown("---")
    
    # 3 grafik için container
    graf1, graf2, graf3 = st.columns(3)
    
    with graf1:
        st.subheader(" En İyi Senaryo")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_iyi["Ay"], 
            y=df_iyi["Toplam Birikim"],
            line=dict(color='#66BB6A', width=3),
            mode='lines'
        ))
        fig1.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                title="Ay"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                title="TL"
            )
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Ek bilgiler
        son_iyi = df_iyi.iloc[-1]
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric(
                label="Toplam Birikim",
                value=f"₺{son_iyi['Toplam Birikim']:,.0f}"
            )
        with col_info2:
            st.metric(
                label="Getiri %",
                value=f"%{(son_iyi['Kar/Zarar']/son_iyi['Toplam Yatırılan']*100):.1f}"
            )
    
    with graf2:
        st.subheader(" Ortalama Senaryo")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_orta["Ay"], 
            y=df_orta["Toplam Birikim"],
            line=dict(color='#FFA726', width=3),
            mode='lines'
        ))
        fig2.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                title="Ay"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                title="TL"
            )
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Ek bilgiler
    
    
    
 son_orta = df_orta.iloc[-1]

        col_info3, col_info4 = st.columns(2)
        with col_info3:
            st.metric(
                label="Toplam Birikim",
                value=f"₺{son_orta['Toplam Birikim']:,.0f}"
            )
        with col_info4:
            st.metric(
                label="Getiri %",
                value=f"%{(son_orta['Kar/Zarar']/son_orta['Toplam Yatırılan']*100):.1f}"
            )

with graf3:
        st.subheader(" Kötü Senaryo")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_kotu["Ay"], 
            y=df_kotu["Toplam Birikim"],
            line=dict(color='#EF5350', width=3),
            mode='lines'
        ))
        fig3.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                title="Ay"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                title="TL"
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Ek bilgiler
        son_kotu = df_kotu.iloc[-1]
        col_info5, col_info6 = st.columns(2)
        with col_info5:
            st.metric(
                label="Toplam Birikim",
                value=f"₺{son_kotu['Toplam Birikim']:,.0f}"
            )
        with col_info6:
            st.metric(
                label="Getiri %",
                value=f"%{(son_kotu['Kar/Zarar']/son_kotu['Toplam Yatırılan']*100):.1f}"
            )

# =========================
# SAĞ SİDEBAR - YATIRIM ÖZETİ
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader(" Yatırım Özeti")

# Yatırım özeti bilgileri
st.sidebar.markdown("###  Son Durum")

# En İyi Senaryo
son_iyi = df_iyi.iloc[-1]
st.sidebar.markdown(f"**En İyi Senaryo:**")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    st.sidebar.metric(
        label="Birikim",
        value=f"₺{son_iyi['Toplam Birikim']:,.0f}",
        delta=f"₺{son_iyi['Kar/Zarar']:,.0f}"
    )
with col_s2:
    getiri_yuzde_iyi = (son_iyi['Kar/Zarar'] / son_iyi['Toplam Yatırılan']) * 100 if son_iyi['Toplam Yatırılan'] > 0 else 0
    st.sidebar.metric(
        label="Getiri %",
        value=f"%{getiri_yuzde_iyi:.1f}"
    )

st.sidebar.markdown(f"*Yatırılan: ₺{son_iyi['Toplam Yatırılan']:,.0f}*")

# Ortalama Senaryo
son_orta = df_orta.iloc[-1]
st.sidebar.markdown(f"**Ortalama Senaryo:**")
col_s3, col_s4 = st.sidebar.columns(2)
with col_s3:
    st.sidebar.metric(
        label="Birikim",
        value=f"₺{son_orta['Toplam Birikim']:,.0f}",
        delta=f"₺{son_orta['Kar/Zarar']:,.0f}"
    )
with col_s4:
    getiri_yuzde_orta = (son_orta['Kar/Zarar'] / son_orta['Toplam Yatırılan']) * 100 if son_orta['Toplam Yatırılan'] > 0 else 0
    st.sidebar.metric(
        label="Getiri %",
        value=f"%{getiri_yuzde_orta:.1f}"
    )

st.sidebar.markdown(f"*Yatırılan: ₺{son_orta['Toplam Yatırılan']:,.0f}*")

# Kötü Senaryo
son_kotu = df_kotu.iloc[-1]
st.sidebar.markdown(f"**Kötü Senaryo:**")
col_s5, col_s6 = st.sidebar.columns(2)
with col_s5:
    st.sidebar.metric(
        label="Birikim",
        value=f"₺{son_kotu['Toplam Birikim']:,.0f}",
        delta=f"₺{son_kotu['Kar/Zarar']:,.0f}"
    )
with col_s6:
    getiri_yuzde_kotu = (son_kotu['Kar/Zarar'] / son_kotu['Toplam Yatırılan']) * 100 if son_kotu['Toplam Yatırılan'] > 0 else 0
    st.sidebar.metric(
        label="Getiri %",
        value=f"%{getiri_yuzde_kotu:.1f}"
    )

st.sidebar.markdown(f"*Yatırılan: ₺{son_kotu['Toplam Yatırılan']:,.0f}*")

# Genel Özet
st.sidebar.markdown("---")
st.sidebar.markdown("###  Genel Özet")

st.sidebar.markdown(f"""
**Başlangıç:** ₺{baslangic:,.0f}

**Süre:** {ay_sayisi} ay

**Varsayılan Aylık Ek:** ₺{aylik_ek_varsayilan:,.0f}

**Ek Yatırım Aralıkları:** {len(ek_yatirimlar)}
""")

# =========================
# ALT KISIM - EK TABLO
# =========================
st.markdown("---")
st.subheader(" Tüm Senaryoların Detaylı Tablosu")

# 3 senaryoyu birleştiren tablo
comparison_df = pd.DataFrame({
    'Ay': df_orta['Ay'],
    'En İyi Birikim': df_iyi['Toplam Birikim'],
    'Ortalama Birikim': df_orta['Toplam Birikim'],
    'Kötü Birikim': df_kotu['Toplam Birikim'],
    'En İyi Kar/Zarar': df_iyi['Kar/Zarar'],
    'Ortalama Kar/Zarar': df_orta['Kar/Zarar'],
    'Kötü Kar/Zarar': df_kotu['Kar/Zarar']
})

st.dataframe(comparison_df, height=300, use_container_width=True)

# CSS for better formatting
st.markdown("""
<style>
    /* Grafik başlıkları */
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metrik kartları için */
    .stMetric {
        background-color: rgba(240, 242, 246, 0.7);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .stMetric label {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar metrikleri */
    .sidebar .stMetric {
        padding: 8px;
        margin: 3px 0;
    }
    
    .sidebar .stMetric label {
        font-size: 0.85rem !important;
    }
    
    .sidebar div[data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }
    
    /* Genel düzen */
    .main > div {
        padding-top: 0.5rem;
    }
    
    /* Divider */
    hr {
        margin: 1rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)
# ... mevcut kodların ...

# =========================
# ALT KISIM - EK TABLO
# =========================
st.markdown("---")
st.subheader("📊 Tüm Senaryoların Detaylı Tablosu")

comparison_df = pd.DataFrame({
    'Ay': df_orta['Ay'],
    'En İyi Birikim': df_iyi['Toplam Birikim'],
    'Ortalama Birikim': df_orta['Toplam Birikim'],
    'Kötü Birikim': df_kotu['Toplam Birikim'],
    'En İyi Kar/Zarar': df_iyi['Kar/Zarar'],
    'Ortalama Kar/Zarar': df_orta['Kar/Zarar'],
    'Kötü Kar/Zarar': df_kotu['Kar/Zarar']
})

st.dataframe(comparison_df, height=300, use_container_width=True)

