import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Dashboard TB Sumbawa", layout="wide")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv('data/tb_sumbawa_clean.csv')

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🔍 Filter Data")

kecamatan = st.sidebar.selectbox(
    "Pilih Kecamatan",
    ["Semua"] + sorted(df['kecamatan'].unique())
)

if kecamatan != "Semua":
    df = df[df['kecamatan'] == kecamatan]

# =========================
# HEADER
# =========================
st.title("📊 Dashboard Monitoring Tuberkulosis")
st.caption("Kabupaten Sumbawa Tahun 2024")

# =========================
# KPI
# =========================
total_kasus = int(df['kasus'].sum())
total_pengobatan = int(df['pengobatan'].sum())
avg_rate = df['complete_rate'].mean()

col1, col2, col3 = st.columns(3)

col1.metric("🦠 Total Kasus", f"{total_kasus:,}")
col2.metric("💊 Total Pengobatan", f"{total_pengobatan:,}")
col3.metric("📈 Avg Complete Rate", f"{avg_rate:.2f}%")

st.divider()

# =========================
# COMPLETE RATE (FULL)
# =========================
st.subheader("📊 Complete Rate per Puskesmas")

fig_full = px.bar(
    df.sort_values(by='complete_rate', ascending=True),
    x='complete_rate',
    y='puskesmas',
    orientation='h',
    color='kategori',
    color_discrete_map={
        'Baik': 'green',
        'Sedang': 'orange',
        'Rendah': 'red'
    },
    text='complete_rate'
)

fig_full.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_full.update_layout(height=600)

st.plotly_chart(fig_full, use_container_width=True)

st.divider()

# =========================
# DISTRIBUSI (FULL WIDTH)
# =========================
st.subheader("📊 Distribusi Kategori Kinerja")

kategori = df['kategori'].value_counts().reset_index()
kategori.columns = ['kategori', 'jumlah']

fig_dist = px.bar(
    kategori,
    x='kategori',
    y='jumlah',
    color='kategori',
    color_discrete_map={
        'Baik': 'green',
        'Sedang': 'orange',
        'Rendah': 'red'
    },
    text='jumlah'
)

fig_dist.update_traces(textposition='outside')

st.plotly_chart(fig_dist, use_container_width=True)

st.divider()

# =========================
# TOP 5 TERBAIK
# =========================
st.subheader("🟢 Top 5 Puskesmas Terbaik")

top5 = df.sort_values(by='complete_rate', ascending=False).head(5)

fig_top = px.bar(
    top5,
    x='complete_rate',
    y='puskesmas',
    orientation='h',
    color='complete_rate',
    color_continuous_scale='greens',
    text='complete_rate'
)

fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_top.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig_top, use_container_width=True)

# =========================
# TOP 5 TERBURUK
# =========================
st.subheader("🔴 Top 5 Puskesmas Terendah")

worst5 = df.sort_values(by='complete_rate').head(5)

fig_worst = px.bar(
    worst5,
    x='complete_rate',
    y='puskesmas',
    orientation='h',
    color='complete_rate',
    color_continuous_scale='reds',
    text='complete_rate'
)

fig_worst.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_worst.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig_worst, use_container_width=True)

st.divider()

# =========================
# DATA DETAIL + TAB
# =========================
st.subheader("📋 Data Detail")

tab1, tab2, tab3, tab4 = st.tabs(["Semua", "Baik", "Sedang", "Rendah"])

with tab1:
    st.dataframe(df.sort_values(by='complete_rate', ascending=False))

with tab2:
    st.dataframe(df[df['kategori']=="Baik"])

with tab3:
    st.dataframe(df[df['kategori']=="Sedang"])

with tab4:
    st.dataframe(df[df['kategori']=="Rendah"])

st.divider()

# =========================
# DATA QUALITY
# =========================
st.subheader("🧪 Evaluasi Kualitas Data")

valid_logic = (df['pengobatan'] <= df['kasus']) & (df['kasus'] > 0)
accuracy = valid_logic.mean() * 100

total_cells = df.shape[0] * df.shape[1]
missing_cells = df.isnull().sum().sum()
completeness = (1 - (missing_cells / total_cells)) * 100

duplicate_rows = df.duplicated().sum()
consistency = (1 - (duplicate_rows / len(df))) * 100

timeliness = "Tidak tersedia"

c1, c2, c3, c4 = st.columns(4)

c1.metric("Accuracy", f"{accuracy:.2f}%")
c2.metric("Completeness", f"{completeness:.2f}%")
c3.metric("Consistency", f"{consistency:.2f}%")
c4.metric("Timeliness", timeliness)

st.warning("⚠️ Timeliness tidak dapat diukur karena dataset tidak memiliki timestamp.")

# =========================
# INSIGHT
# =========================
st.subheader("📌 Insight Utama")

kategori_terbanyak = df['kategori'].value_counts().idxmax()

st.markdown(f"""
- Total kasus: **{total_kasus}**
- Rata-rata keberhasilan: **{avg_rate:.2f}%**
- Mayoritas kategori: **{kategori_terbanyak}**
- Prioritas: puskesmas dengan complete rate < 50%
""")