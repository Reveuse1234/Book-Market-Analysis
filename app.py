"""
app.py – Amazon India Book Market Analysis Dashboard
=====================================================
Run:  python3 -m streamlit run app.py

Pages
-----
0. Home              – project introduction and navigation guide
1. Market Overview   – key statistics and overall market trends
2. Book & Genre Analysis – compare genres, prices, ratings, formats
3. Insights          – data-backed patterns and observations
"""

import streamlit as st
import pandas as pd
import plotly.express as px

import data_loader as dl
import analysis    as an

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Book Market Analysis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f0f4f8; }
[data-testid="stSidebar"]          { background: #1e2a3a; }
[data-testid="stSidebar"] *        { color: #e2e8f0 !important; }

/* home page */
.home-hero {
    background: linear-gradient(135deg, #1e2a3a 0%, #2563EB 100%);
    border-radius: 14px;
    padding: 48px 40px;
    margin-bottom: 28px;
    color: #ffffff;
}
.home-hero h1 { font-size: 2.4rem; font-weight: 800; margin:0 0 8px 0; color:#fff; }
.home-hero p  { font-size: 1.05rem; color: #cbd5e1; margin: 0; line-height: 1.7; }

.home-stat-row { display:flex; gap:16px; flex-wrap:wrap; margin:20px 0 28px 0; }
.home-stat {
    background:#ffffff; border-radius:10px; padding:18px 22px;
    flex:1 1 140px; min-width:130px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);
    text-align:center;
}
.home-stat-val  { font-size:1.7rem; font-weight:800; color:#2563EB; line-height:1.1; }
.home-stat-lbl  { font-size:0.72rem; color:#64748b; margin-top:5px;
                  text-transform:uppercase; letter-spacing:.05em; }

.nav-card-row { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:24px; }
.nav-card {
    background:#ffffff; border-radius:12px; padding:22px 24px;
    flex:1 1 220px; min-width:200px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);
    border-top: 4px solid #2563EB;
}
.nav-card h3  { font-size:1rem; font-weight:700; color:#1e293b; margin:0 0 6px 0; }
.nav-card p   { font-size:.84rem; color:#475569; margin:0; line-height:1.55; }

.dataset-note {
    background:#fffbeb; border:1px solid #fcd34d; border-radius:8px;
    padding:12px 16px; font-size:.85rem; color:#78350f; margin-top:8px;
}

/* KPI cards */
.kpi-row  { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:1.2rem; }
.kpi-card {
    background:#ffffff; border-radius:10px; padding:16px 20px;
    flex:1 1 150px; min-width:140px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);
    border-left:4px solid #2563EB;
}
.kpi-value { font-size:1.45rem; font-weight:700; color:#1e293b; line-height:1.2; }
.kpi-label { font-size:0.73rem; color:#64748b; margin-top:4px;
             text-transform:uppercase; letter-spacing:.04em; }

/* section dividers */
.section-hdr {
    font-size:1.1rem; font-weight:700; color:#1e293b;
    margin:1.4rem 0 .5rem 0;
    padding-bottom:5px;
    border-bottom:2px solid #2563EB;
}

/* insight cards */
.ins-positive { background:#f0fdf4; border-left:4px solid #16a34a;
                border-radius:8px; padding:12px 16px; margin-bottom:10px; }
.ins-warning  { background:#fff7ed; border-left:4px solid #ea580c;
                border-radius:8px; padding:12px 16px; margin-bottom:10px; }
.ins-neutral  { background:#eff6ff; border-left:4px solid #2563EB;
                border-radius:8px; padding:12px 16px; margin-bottom:10px; }
.ins-title    { font-weight:700; font-size:.97rem; margin-bottom:4px; color:#1e293b; }
.ins-body     { font-size:.87rem; color:#374151; line-height:1.65; }

/* data quality badge */
.dq-row { display:flex; gap:10px; flex-wrap:wrap; margin:10px 0 16px 0; }
.dq-badge {
    background:#fff; border-radius:8px; padding:10px 16px;
    flex:1 1 160px; min-width:150px;
    box-shadow:0 1px 3px rgba(0,0,0,0.07);
    border-left:3px solid #94a3b8;
    font-size:.85rem; color:#374151;
}
.dq-badge strong { color:#1e293b; display:block; font-size:1.1rem; }

#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Data loading (cached)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Loading and cleaning dataset…")
def get_data():
    df              = dl.load_clean()
    raw, genres, _  = dl.load_raw()
    by_genre        = an.summary_by_genre(df)
    by_type         = an.summary_by_type(df)
    top_reviewed    = an.top_books_by_reviews(df, 10)
    top_rated       = an.top_books_by_rating(df, min_reviews=500, n=10)
    price_df        = an.price_distribution(df)
    kpis            = an.summary_overall(df)
    insights        = an.market_insights(df, by_genre, by_type)
    return df, raw, genres, by_genre, by_type, top_reviewed, top_rated, price_df, kpis, insights


(df, raw_df, genres_df,
 by_genre, by_type,
 top_reviewed, top_rated,
 price_df, kpis, insights) = get_data()

audit = df.attrs.get("audit", {})


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Book Market Analysis")
    st.markdown("**Amazon India Best Sellers**")
    st.caption(
        "Dataset: scraped catalogue data.  \n"
        "Contains: titles, authors, genres, formats, prices, ratings, "
        "and review counts.  \n"
        "⚠️ No sales or revenue data is available."
    )
    st.divider()

    pages = ["🏠 Home", "📈 Market Overview", "📊 Book & Genre Analysis", "💡 Insights"]
    page = st.radio("Navigate", pages, label_visibility="collapsed")

    st.divider()
    st.markdown("### 🔧 Filters")

    genre_filter = st.multiselect(
        "Genre(s)", options=sorted(df["Main Genre"].unique()),
        default=[], placeholder="All genres",
    )
    type_filter = st.multiselect(
        "Format(s)", options=sorted(df["Type"].unique()),
        default=[], placeholder="All formats",
    )
    price_range = st.slider(
        "Price Range (₹)",
        min_value=int(df["Price (INR)"].min()),
        max_value=int(df["Price (INR)"].max()),
        value=(int(df["Price (INR)"].min()), int(df["Price (INR)"].max())),
    )
    rating_range = st.slider(
        "Rating Range",
        min_value=float(df["Rating"].min()),
        max_value=5.0,
        value=(float(df["Rating"].min()), 5.0),
        step=0.1,
    )
    st.divider()
    st.caption("Source: archive.zip / Amazon Books Scraping")


# ─────────────────────────────────────────────────────────────────────────────
# Apply filters
# ─────────────────────────────────────────────────────────────────────────────
fdf = df.copy()
if genre_filter:
    fdf = fdf[fdf["Main Genre"].isin(genre_filter)]
if type_filter:
    fdf = fdf[fdf["Type"].isin(type_filter)]
fdf = fdf[
    fdf["Price (INR)"].between(*price_range) &
    fdf["Rating"].between(*rating_range)
]

f_by_genre   = an.summary_by_genre(fdf)
f_by_type    = an.summary_by_type(fdf)
f_kpis       = an.summary_overall(fdf)
f_price_df   = an.price_distribution(fdf)
f_insights   = an.market_insights(fdf, f_by_genre, f_by_type)

filters_active = bool(genre_filter or type_filter
                      or price_range != (int(df["Price (INR)"].min()), int(df["Price (INR)"].max()))
                      or rating_range != (float(df["Rating"].min()), 5.0))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def fmt_price(v: float) -> str:
    return f"₹{v:,.0f}"

def fmt_big(v: float) -> str:
    if v >= 1e7:  return f"{v/1e7:.1f} Cr"
    if v >= 1e5:  return f"{v/1e5:.1f} L"
    if v >= 1e3:  return f"{v/1e3:.0f}K"
    return str(int(v))

def kpi(label: str, value: str) -> str:
    return (
        f'<div class="kpi-card">'
        f'  <div class="kpi-value">{value}</div>'
        f'  <div class="kpi-label">{label}</div>'
        f'</div>'
    )

def render_kpis(k: dict):
    html = '<div class="kpi-row">'
    html += kpi("Total Books",         f"{k['Total Books']:,}")
    html += kpi("Genres",              f"{k['Total Genres']}")
    html += kpi("Sub-Genres",          f"{k['Total Sub-Genres']}")
    html += kpi("Authors",             f"{k['Total Authors']:,}")
    html += kpi("Avg Price",           f"₹{k['Avg Price (INR)']:.0f}")
    html += kpi("Median Price",        f"₹{k['Median Price (INR)']:.0f}")
    html += kpi("Avg Rating",          f"{k['Avg Rating']:.2f} / 5")
    html += kpi("Total Reviews",       fmt_big(k['Total Reviews']))
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def section(title: str):
    st.markdown(f'<div class="section-hdr">{title}</div>', unsafe_allow_html=True)

def insight_card(ins: dict):
    css = f"ins-{ins['type']}"
    st.markdown(
        f'<div class="{css}">'
        f'  <div class="ins-title">{ins["title"]}</div>'
        f'  <div class="ins-body">{ins["body"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Page 0 — Home
# ─────────────────────────────────────────────────────────────────────────────
if page == pages[0]:
    st.markdown("""
    <div class="home-hero">
        <h1>📚 Book Market Analysis</h1>
        <p>
            An exploratory analysis of the <strong>Amazon India Books Best Sellers</strong> catalogue —
            covering genres, formats, listed prices, reader ratings, and review counts.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Dataset at-a-glance stats
    st.markdown(f"""
    <div class="home-stat-row">
        <div class="home-stat">
            <div class="home-stat-val">{kpis['Total Books']:,}</div>
            <div class="home-stat-lbl">Books</div>
        </div>
        <div class="home-stat">
            <div class="home-stat-val">{kpis['Total Genres']}</div>
            <div class="home-stat-lbl">Genres</div>
        </div>
        <div class="home-stat">
            <div class="home-stat-val">{kpis['Total Sub-Genres']}</div>
            <div class="home-stat-lbl">Sub-Genres</div>
        </div>
        <div class="home-stat">
            <div class="home-stat-val">{kpis['Total Authors']:,}</div>
            <div class="home-stat-lbl">Authors</div>
        </div>
        <div class="home-stat">
            <div class="home-stat-val">₹{kpis['Avg Price (INR)']:.0f}</div>
            <div class="home-stat-lbl">Avg Listed Price</div>
        </div>
        <div class="home-stat">
            <div class="home-stat-val">{kpis['Avg Rating']:.2f}</div>
            <div class="home-stat-lbl">Avg Rating / 5</div>
        </div>
        <div class="home-stat">
            <div class="home-stat-val">{fmt_big(kpis['Total Reviews'])}</div>
            <div class="home-stat-lbl">Total Reviews</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dataset note
    st.markdown("""
    <div class="dataset-note">
        ⚠️ <strong>Dataset note:</strong> This is a scraped Amazon India catalogue snapshot.
        It contains listed prices, ratings, and review counts only.
        It does <strong>not</strong> contain sales figures, revenue, or units sold.
        Review counts reflect the number of Amazon reviews on each listing — they are not a proxy for purchases.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation guide cards
    section("🗂️ What's in this Dashboard")
    st.markdown("""
    <div class="nav-card-row">
        <div class="nav-card">
            <h3>📈 Market Overview</h3>
            <p>Key statistics, data quality summary, catalogue distribution by genre,
            total reviews by genre, rating histogram, and price band distribution.</p>
        </div>
        <div class="nav-card">
            <h3>📊 Book & Genre Analysis</h3>
            <p>Detailed price and rating comparisons across genres and formats,
            most-reviewed books, highest-rated books, price vs rating scatter,
            and a genre comparison heatmap.</p>
        </div>
        <div class="nav-card">
            <h3>💡 Insights</h3>
            <p>Data-backed observations on catalogue size, review patterns,
            pricing, and format distribution — each grounded in a specific
            measured value from the dataset.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# Page 1 — Market Overview
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[1]:
    st.title("📚 Book Market Analysis")
    st.markdown(
        "Analysing the **Amazon India Best Sellers** catalogue.  "
        "This dataset contains scraped listing data: titles, authors, genres, "
        "formats, prices, ratings, and review counts.  \n"
        "> ℹ️ **Note:** This dataset does not contain actual sales or revenue figures.  "
        "All metrics are based on catalogue data and reader reviews."
    )

    if filters_active:
        st.info(f"🔧 Filters active — showing **{len(fdf):,}** of **{len(df):,}** books.")

    section("📌 Key Market Statistics")
    render_kpis(f_kpis)

    # Data quality panel
    section("🧹 Dataset & Data Quality")
    if audit:
        dq_html = '<div class="dq-row">'
        dq_html += f'<div class="dq-badge"><strong>{audit["final_rows"]:,}</strong> Clean records</div>'
        dq_html += f'<div class="dq-badge"><strong>21</strong> Missing authors → filled "Unknown"</div>'
        dq_html += f'<div class="dq-badge"><strong>{audit["dropped_price"]}</strong> Unparseable prices dropped</div>'
        dq_html += f'<div class="dq-badge"><strong>{audit["dropped_reviews"]}</strong> Zero-review rows dropped</div>'
        dq_html += f'<div class="dq-badge"><strong>{audit["dropped_dupes"]}</strong> Duplicate entries removed</div>'
        dq_html += '</div>'
        st.markdown(dq_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        section("📚 Catalogue by Genre")
        st.plotly_chart(an.fig_books_by_genre(f_by_genre), use_container_width=True)
    with col2:
        section("📖 Catalogue Share (Top 12 Genres)")
        st.plotly_chart(an.fig_books_by_genre_pie(f_by_genre), use_container_width=True)

    section("💬 Total Reviews by Genre")
    st.plotly_chart(an.fig_reviews_by_genre(f_by_genre), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section("⭐ Rating Distribution")
        st.plotly_chart(an.fig_rating_distribution(fdf), use_container_width=True)
    with col4:
        section("💵 Books per Price Band")
        st.plotly_chart(an.fig_price_distribution(f_price_df), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Page 2 — Book & Genre Analysis
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[2]:
    st.title("📊 Book & Genre Analysis")
    st.markdown(
        "Compare genres, prices, ratings, and formats across the catalogue.  "
        "Use the sidebar filters to narrow down the view."
    )

    if filters_active:
        st.info(f"🔧 Filters active — showing **{len(fdf):,}** of **{len(df):,}** books.")

    # ── Prices ────────────────────────────────────────────────────────────────
    section("💰 Pricing Analysis")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Price",    f"₹{fdf['Price (INR)'].min():.2f}")
    col2.metric("Avg Price",    f"₹{fdf['Price (INR)'].mean():.2f}")
    col3.metric("Median Price", f"₹{fdf['Price (INR)'].median():.2f}")
    col4.metric("Max Price",    f"₹{fdf['Price (INR)'].max():.2f}")

    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(an.fig_avg_price_by_genre(f_by_genre), use_container_width=True)
    with col6:
        st.plotly_chart(an.fig_price_by_type(f_by_type), use_container_width=True)

    section("🔍 Price vs Rating  (bubble size = review count)")
    st.plotly_chart(an.fig_price_vs_rating(fdf), use_container_width=True)

    # ── Ratings ───────────────────────────────────────────────────────────────
    section("⭐ Rating Analysis")
    col7, col8, col9, col10 = st.columns(4)
    col7.metric("Avg Rating",    f"{fdf['Rating'].mean():.2f} / 5")
    col8.metric("Median Rating", f"{fdf['Rating'].median():.2f}")
    col9.metric("Books ≥ 4.5",   f"{(fdf['Rating'] >= 4.5).sum():,}")
    col10.metric("Books < 3.5",  f"{(fdf['Rating'] < 3.5).sum():,}")

    col11, col12 = st.columns(2)
    with col11:
        st.plotly_chart(an.fig_avg_rating_by_genre(f_by_genre), use_container_width=True)
    with col12:
        rb = an.rating_bins(fdf)
        fig_rb = px.bar(
            rb, x="Rating Band", y="Books",
            color="Books", color_continuous_scale="Greens",
            title="Books per Rating Bracket", text="Books",
        )
        fig_rb.update_traces(textposition="outside")
        fig_rb.update_layout(coloraxis_showscale=False, height=420)
        st.plotly_chart(fig_rb, use_container_width=True)

    # ── Formats ───────────────────────────────────────────────────────────────
    section("📦 Format Analysis")
    col13, col14 = st.columns(2)
    with col13:
        st.plotly_chart(an.fig_books_by_type(f_by_type), use_container_width=True)
    with col14:
        # format price + rating dual axis
        import plotly.graph_objects as go
        top8 = f_by_type.sort_values("Books", ascending=False).head(8)
        fig_dual = go.Figure()
        fig_dual.add_trace(go.Bar(
            name="Avg Price (₹)", x=top8["Type"], y=top8["Avg Price (INR)"],
            marker_color="#2563EB",
        ))
        fig_dual.add_trace(go.Scatter(
            name="Avg Rating", x=top8["Type"], y=top8["Avg Rating"],
            mode="lines+markers", yaxis="y2",
            marker=dict(size=8, color="#16a34a"),
            line=dict(color="#16a34a", width=2),
        ))
        fig_dual.update_layout(
            title="Price & Rating by Format (Top 8)",
            yaxis=dict(title="Avg Price (₹)"),
            yaxis2=dict(title="Avg Rating", overlaying="y", side="right", range=[3, 5]),
            xaxis_tickangle=-25, height=430,
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_dual, use_container_width=True)

    # ── Top books ─────────────────────────────────────────────────────────────
    section("🏆 Most-Reviewed Books")
    n_top = st.slider("Number of books", 5, 30, 10, key="top_n")
    f_top_rev = an.top_books_by_reviews(fdf, n_top)
    st.plotly_chart(an.fig_top_by_reviews(f_top_rev), use_container_width=True)

    section("⭐ Highest-Rated Books (min 500 reviews)")
    f_top_rat = an.top_books_by_rating(fdf, min_reviews=500, n=n_top)
    display_rat = f_top_rat.copy()
    display_rat["Price (INR)"]    = display_rat["Price (INR)"].apply(lambda v: f"₹{v:.2f}")
    display_rat["Review Count"]   = display_rat["Review Count"].apply(lambda v: f"{v:,.0f}")
    display_rat.index = range(1, len(display_rat) + 1)
    st.dataframe(display_rat, use_container_width=True)

    # ── Genre comparison heatmap ──────────────────────────────────────────────
    section("🗺️ Genre Comparison Heatmap")
    st.caption("Scores are normalised per column: 0 = lowest in dataset, 1 = highest.")
    st.plotly_chart(an.fig_genre_heatmap(fdf), use_container_width=True)

    # ── Genre summary table ───────────────────────────────────────────────────
    section("📋 Genre Summary Table")
    display_genre = f_by_genre.copy()
    display_genre["Avg Price (INR)"]    = display_genre["Avg Price (INR)"].apply(lambda v: f"₹{v:.2f}")
    display_genre["Median Price (INR)"] = display_genre["Median Price (INR)"].apply(lambda v: f"₹{v:.2f}")
    display_genre["Avg Rating"]         = display_genre["Avg Rating"].apply(lambda v: f"{v:.2f}")
    display_genre["Total Reviews"]      = display_genre["Total Reviews"].apply(lambda v: f"{v:,.0f}")
    display_genre["Avg Reviews"]        = display_genre["Avg Reviews"].apply(lambda v: f"{v:,.0f}")
    display_genre.index = range(1, len(display_genre) + 1)
    st.dataframe(display_genre, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Page 3 — Insights
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[3]:
    st.title("💡 Market Insights")
    st.markdown(
        "Patterns and observations derived directly from the dataset.  \n"
        "> ℹ️ All findings are grounded in the available data fields: "
        "**price, rating, review count, genre, and format**.  "
        "No sales or revenue claims are made."
    )

    if filters_active:
        st.info(f"🔧 Filters active — showing **{len(fdf):,}** of **{len(df):,}** books.")

    for ins in f_insights:
        insight_card(ins)

    st.divider()
    section("📊 Supporting Charts")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(an.fig_avg_rating_by_genre(f_by_genre), use_container_width=True)
    with col2:
        st.plotly_chart(an.fig_avg_price_by_genre(f_by_genre), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(an.fig_reviews_by_genre(f_by_genre), use_container_width=True)
    with col4:
        st.plotly_chart(an.fig_price_distribution(f_price_df), use_container_width=True)

    section("🗂️ Raw Data Explorer")
    search = st.text_input("🔎 Search by title or author", "")
    view = fdf.copy()
    if search:
        mask = (
            view["Title"].str.contains(search, case=False, na=False) |
            view["Author"].str.contains(search, case=False, na=False)
        )
        view = view[mask]
        st.caption(f"Found {len(view):,} matching records.")

    cols = ["Title", "Author", "Main Genre", "Sub Genre",
            "Type", "Price (INR)", "Rating", "Review Count"]
    display = view[cols].copy()
    display["Price (INR)"]  = display["Price (INR)"].apply(lambda v: f"₹{v:.2f}")
    display["Review Count"] = display["Review Count"].apply(lambda v: f"{v:,.0f}")
    display = display.reset_index(drop=True)
    display.index = range(1, len(display) + 1)
    st.dataframe(display, use_container_width=True, height=480)

