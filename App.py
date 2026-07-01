import streamlit as st
import pandas as pd
import plotly.express as px

# ─── CONFIG ───────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")
st.title("📊 Sales Performance Dashboard")
st.markdown("---")

# ─── LOAD DATA ────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("sales.csv")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    return df

df = load_data()

# ─── SIDEBAR FILTER ───────────────────────────────────────
st.sidebar.header("🔍 Filter Data")

# Filter tahun
tahun = st.sidebar.multiselect(
    "Tahun",
    options=sorted(df["Tanggal"].dt.year.unique()),
    default=sorted(df["Tanggal"].dt.year.unique())
)

# Filter kategori
kategori = st.sidebar.multiselect(
    "Kategori",
    options=df["Kategori"].unique(),
    default=df["Kategori"].unique()
)

# Filter region
region = st.sidebar.multiselect(
    "Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Filter Status
status = st.sidebar.multiselect(
    "status" , 
    options=df["Status"].unique(),
    default=df["Status"].unique()
)

# Apply filter
df_filtered = df[
    (df["Tanggal"].dt.year.isin(tahun)) &
    (df["Kategori"].isin(kategori)) &
    (df["Region"].isin(region)) &
    (df["Status"].isin(status))
]

# ─── KPI CARDS ────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = df_filtered["Revenue"].sum()
total_profit  = df_filtered["Profit"].sum()
total_order   = len(df_filtered)
avg_order     = df_filtered["Revenue"].mean()
profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0

col1.metric("💰 Total Revenue",  f"Rp {total_revenue:,.0f}")
col2.metric("📈 Total Profit",   f"Rp {total_profit:,.0f}")
col3.metric("🛒 Total Order",    f"{total_order:,}")
col4.metric("🧾 Rata-rata Order", f"Rp {avg_order:,.0f}")
col5.metric("% Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")

# ─── CHARTS ROW 1 ─────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📅 Tren Revenue per Bulan")
    tren = (
        df_filtered
        .groupby(df_filtered["Tanggal"].dt.to_period("M"))["Revenue"]
        .sum()
        .reset_index()
    )
    tren["Tanggal"] = tren["Tanggal"].astype(str)
    fig1 = px.line(tren, x="Tanggal", y="Revenue", markers=True,
                   color_discrete_sequence=["#636E12"])
    fig1.update_layout(xaxis_title="Bulan", yaxis_title="Revenue (Rp)")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("🏆 Revenue per Kategori")
    cat_rev = df_filtered.groupby("Kategori")["Revenue"].sum().reset_index()
    fig2 = px.bar(cat_rev.sort_values("Revenue", ascending=True),
                  x="Revenue", y="Kategori", orientation="h",
                  color="Revenue", color_continuous_scale="Blues")
    fig2.update_layout(xaxis_title="Revenue (Rp)", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

# ─── CHARTS ROW 2 ─────────────────────────────────────────
col_c, col_d, col_e = st.columns(3)

with col_c:
    st.subheader("🗺️ Revenue per Region")
    reg_rev = df_filtered.groupby("Region")["Revenue"].sum().reset_index()
    fig3 = px.pie(reg_rev, values="Revenue", names="Region", hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("📦 Top 10 Produk Terlaris")
    top_prod = (
        df_filtered.groupby("Produk")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig4 = px.bar(top_prod.sort_values("Revenue"),
                  x="Revenue", y="Produk", orientation="h",
                  color="Revenue", color_continuous_scale="Greens")
    fig4.update_layout(xaxis_title="Revenue (Rp)", yaxis_title="")
    st.plotly_chart(fig4, use_container_width=True)

with col_e:
    st.subheader("💰 Revenue vs Profit per Kategori")
    grouped = df_filtered.groupby("Kategori")[["Revenue", "Profit"]].sum().reset_index()
    grouped_melt = grouped.melt(id_vars="Kategori", var_name="Tipe", value_name="Nilai")
    fig5 = px.bar(grouped_melt, x="Kategori", y="Nilai", color="Tipe", barmode="group")
    fig5.update_layout(xaxis_title="Kategori", yaxis_title="Nilai (Rp)")
    st.plotly_chart(fig5, use_container_width=True)

# ─── DATA TABLE ───────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Detail Transaksi")
st.dataframe(
    df_filtered.sort_values("Tanggal", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=300
)

st.caption(f"Menampilkan {len(df_filtered):,} dari {len(df):,} transaksi")