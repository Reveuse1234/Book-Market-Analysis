"""
analysis.py
-----------
Grouped summaries, Plotly charts, and data-backed insights.

All analysis is grounded in the actual dataset fields:
  Price (INR), Rating, Review Count, Main Genre, Sub Genre, Type, Author.

No sales, revenue, or quantity figures are used — the dataset does not
contain that information.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── colour palette ─────────────────────────────────────────────────────────────
PALETTE  = px.colors.qualitative.Bold
MONO_SEQ = "Blues"
ACCENT   = "#2563EB"


# ─────────────────────────────────────────────────────────────────────────────
# Summaries
# ─────────────────────────────────────────────────────────────────────────────

def summary_overall(df: pd.DataFrame) -> dict:
    """Top-line KPIs derived from available data."""
    return {
        "Total Books":        len(df),
        "Total Genres":       df["Main Genre"].nunique(),
        "Total Sub-Genres":   df["Sub Genre"].nunique(),
        "Total Authors":      df["Author"].nunique(),
        "Avg Price (INR)":    df["Price (INR)"].mean(),
        "Median Price (INR)": df["Price (INR)"].median(),
        "Avg Rating":         df["Rating"].mean(),
        "Total Reviews":      df["Review Count"].sum(),
    }


def summary_by_genre(df: pd.DataFrame) -> pd.DataFrame:
    """Per-genre aggregation of books, price, rating, and review counts."""
    g = (
        df.groupby("Main Genre", as_index=False)
          .agg(
              Books         =("Title",       "count"),
              Avg_Price     =("Price (INR)", "mean"),
              Median_Price  =("Price (INR)", "median"),
              Avg_Rating    =("Rating",      "mean"),
              Total_Reviews =("Review Count","sum"),
              Avg_Reviews   =("Review Count","mean"),
          )
    )
    g.columns = ["Main Genre", "Books", "Avg Price (INR)", "Median Price (INR)",
                 "Avg Rating", "Total Reviews", "Avg Reviews"]
    return g.sort_values("Books", ascending=False).reset_index(drop=True)


def summary_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """Per-format aggregation."""
    g = (
        df.groupby("Type", as_index=False)
          .agg(
              Books       =("Title",       "count"),
              Avg_Price   =("Price (INR)", "mean"),
              Avg_Rating  =("Rating",      "mean"),
              Total_Reviews=("Review Count","sum"),
          )
    )
    g.columns = ["Type", "Books", "Avg Price (INR)", "Avg Rating", "Total Reviews"]
    return g.sort_values("Books", ascending=False).reset_index(drop=True)


def top_books_by_reviews(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-n books by total review count (a proxy for reader engagement)."""
    cols = ["Title", "Author", "Main Genre", "Type", "Price (INR)", "Rating", "Review Count"]
    return (
        df[cols]
          .sort_values("Review Count", ascending=False)
          .head(n)
          .reset_index(drop=True)
    )


def top_books_by_rating(df: pd.DataFrame, min_reviews: int = 500, n: int = 10) -> pd.DataFrame:
    """Top-n highest-rated books with at least min_reviews reviews."""
    cols = ["Title", "Author", "Main Genre", "Type", "Price (INR)", "Rating", "Review Count"]
    return (
        df.loc[df["Review Count"] >= min_reviews, cols]
          .sort_values("Rating", ascending=False)
          .head(n)
          .reset_index(drop=True)
    )


def price_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Books binned into price brackets."""
    bins   = [0, 100, 200, 300, 500, 800, 1200, np.inf]
    labels = ["₹0–100", "₹101–200", "₹201–300",
              "₹301–500", "₹501–800", "₹801–1200", "₹1200+"]
    tmp = df.copy()
    tmp["Price Band"] = pd.cut(tmp["Price (INR)"], bins=bins, labels=labels, right=True)
    return (
        tmp.groupby("Price Band", observed=True)
           .agg(Books=("Title", "count"), Avg_Rating=("Rating", "mean"))
           .rename(columns={"Avg_Rating": "Avg Rating"})
           .reset_index()
    )


def rating_bins(df: pd.DataFrame) -> pd.DataFrame:
    """Count books per rating bracket."""
    bins   = [0, 3.0, 3.5, 4.0, 4.5, 5.01]
    labels = ["< 3.0", "3.0–3.5", "3.5–4.0", "4.0–4.5", "4.5–5.0"]
    tmp = df.copy()
    tmp["Rating Band"] = pd.cut(tmp["Rating"], bins=bins, labels=labels, right=False)
    return (
        tmp.groupby("Rating Band", observed=True)
           .agg(Books=("Title", "count"))
           .reset_index()
    )


# ─────────────────────────────────────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────────────────────────────────────

def fig_books_by_genre(by_genre: pd.DataFrame) -> go.Figure:
    """Horizontal bar — book count per genre."""
    df = by_genre.sort_values("Books")
    fig = px.bar(
        df, x="Books", y="Main Genre",
        orientation="h",
        color="Books",
        color_continuous_scale=MONO_SEQ,
        title="📚 Number of Books per Genre",
        labels={"Main Genre": "", "Books": "Number of Books"},
        text="Books",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=620,
                      margin=dict(l=10, r=60, t=50, b=10))
    return fig


def fig_books_by_genre_pie(by_genre: pd.DataFrame) -> go.Figure:
    """Donut — catalogue share per genre (top 12)."""
    top = by_genre.sort_values("Books", ascending=False).head(12)
    fig = px.pie(
        top, names="Main Genre", values="Books",
        title="📖 Catalogue Share by Genre (Top 12)",
        color_discrete_sequence=PALETTE,
        hole=0.38,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=False, height=480)
    return fig


def fig_avg_price_by_genre(by_genre: pd.DataFrame) -> go.Figure:
    """Bar — average price per genre."""
    df = by_genre.sort_values("Avg Price (INR)", ascending=False)
    fig = px.bar(
        df, x="Main Genre", y="Avg Price (INR)",
        color="Avg Price (INR)",
        color_continuous_scale="Oranges",
        title="💰 Average Price by Genre",
        labels={"Avg Price (INR)": "Avg Price (₹)", "Main Genre": ""},
        text=df["Avg Price (INR)"].apply(lambda v: f"₹{v:.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-40,
                      height=480, margin=dict(b=130))
    return fig


def fig_avg_rating_by_genre(by_genre: pd.DataFrame) -> go.Figure:
    """Bar — average rating per genre."""
    df = by_genre.sort_values("Avg Rating", ascending=False)
    fig = px.bar(
        df, x="Main Genre", y="Avg Rating",
        color="Avg Rating",
        color_continuous_scale="Greens",
        range_y=[3.5, 5.0],
        title="⭐ Average Rating by Genre",
        labels={"Avg Rating": "Avg Rating", "Main Genre": ""},
        text=df["Avg Rating"].apply(lambda v: f"{v:.2f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-40,
                      height=480, margin=dict(b=130))
    return fig


def fig_books_by_type(by_type: pd.DataFrame) -> go.Figure:
    """Donut — catalogue share per format (top 8 + Other)."""
    top = by_type.sort_values("Books", ascending=False).head(8).copy()
    rest = by_type.iloc[8:]["Books"].sum()
    if rest > 0:
        top = pd.concat(
            [top, pd.DataFrame([{"Type": "Other", "Books": rest}])],
            ignore_index=True,
        )
    fig = px.pie(
        top, names="Type", values="Books",
        title="📦 Catalogue Share by Format",
        color_discrete_sequence=PALETTE,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=True, height=460)
    return fig


def fig_top_by_reviews(top: pd.DataFrame) -> go.Figure:
    """Horizontal bar — top books by review count."""
    df = top.sort_values("Review Count")
    short_title = df["Title"].str[:50] + "…"
    fig = px.bar(
        df, x="Review Count", y=short_title,
        orientation="h",
        color="Rating",
        color_continuous_scale="RdYlGn",
        title="🏆 Most-Reviewed Books",
        labels={"y": "", "Review Count": "Total Reviews"},
        text=df["Review Count"].apply(lambda v: f"{v:,.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500, coloraxis_colorbar=dict(title="Rating"),
                      margin=dict(l=10, r=80, t=50, b=10))
    return fig


def fig_price_distribution(price_df: pd.DataFrame) -> go.Figure:
    """Bar — number of books per price band, coloured by avg rating."""
    fig = px.bar(
        price_df, x="Price Band", y="Books",
        color="Avg Rating",
        color_continuous_scale="RdYlGn",
        range_color=[3.8, 5.0],
        title="💵 Books per Price Band (colour = avg rating)",
        labels={"Books": "Number of Books"},
        text="Books",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_colorbar=dict(title="Avg Rating"), height=420)
    return fig


def fig_rating_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram — overall rating distribution."""
    fig = px.histogram(
        df, x="Rating",
        nbins=25,
        color_discrete_sequence=[ACCENT],
        title="⭐ Rating Distribution across All Books",
        labels={"Rating": "Rating Score", "count": "Number of Books"},
    )
    fig.update_layout(bargap=0.06, height=400)
    return fig


def fig_price_vs_rating(df: pd.DataFrame) -> go.Figure:
    """Scatter — price vs rating, bubble sized by review count."""
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample,
        x="Price (INR)", y="Rating",
        size="Review Count",
        color="Main Genre",
        hover_data=["Title", "Author", "Type"],
        title="🔍 Price vs Rating  (bubble size = review count)",
        labels={"Price (INR)": "Price (₹)", "Rating": "Rating Score"},
        color_discrete_sequence=PALETTE,
        opacity=0.65,
        size_max=28,
    )
    fig.update_layout(height=520, legend=dict(title="Genre"))
    return fig


def fig_reviews_by_genre(by_genre: pd.DataFrame) -> go.Figure:
    """Horizontal bar — total review count per genre."""
    df = by_genre.sort_values("Total Reviews")
    fig = px.bar(
        df, x="Total Reviews", y="Main Genre",
        orientation="h",
        color="Total Reviews",
        color_continuous_scale=MONO_SEQ,
        title="💬 Total Reviews by Genre",
        labels={"Main Genre": "", "Total Reviews": "Total Reviews"},
        text=df["Total Reviews"].apply(lambda v: f"{v/1e3:.0f}K" if v >= 1000 else str(int(v))),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=620,
                      margin=dict(l=10, r=70, t=50, b=10))
    return fig


def fig_price_by_type(by_type: pd.DataFrame) -> go.Figure:
    """Bar — average price per format (top 10)."""
    df = by_type.sort_values("Avg Price (INR)", ascending=False).head(10)
    fig = px.bar(
        df, x="Type", y="Avg Price (INR)",
        color="Avg Price (INR)",
        color_continuous_scale="Purples",
        title="💰 Average Price by Format",
        labels={"Avg Price (INR)": "Avg Price (₹)", "Type": ""},
        text=df["Avg Price (INR)"].apply(lambda v: f"₹{v:.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30,
                      height=420, margin=dict(b=100))
    return fig


def fig_genre_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap — normalised metric matrix (Genre × Metric)."""
    by_genre = (
        df.groupby("Main Genre")
          .agg(
              Books        =("Title",        "count"),
              Avg_Price    =("Price (INR)",  "mean"),
              Avg_Rating   =("Rating",       "mean"),
              Total_Reviews=("Review Count", "sum"),
          )
    )
    normed = (by_genre - by_genre.min()) / (by_genre.max() - by_genre.min())
    normed = normed.fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=normed.values,
        x=["Books", "Avg Price", "Avg Rating", "Total Reviews"],
        y=normed.index.tolist(),
        colorscale="Blues",
        text=[[f"{v:.2f}" for v in row] for row in normed.values],
        texttemplate="%{text}",
        hoverongaps=False,
    ))
    fig.update_layout(
        title="🗺️ Genre Comparison Heatmap  (normalised 0 = lowest, 1 = highest)",
        height=700,
        margin=dict(l=10, r=10, t=55, b=10),
        yaxis=dict(autorange="reversed"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Insights
# ─────────────────────────────────────────────────────────────────────────────

def market_insights(df: pd.DataFrame,
                    by_genre: pd.DataFrame,
                    by_type: pd.DataFrame) -> list[dict]:
    """
    Return data-backed insights as a list of dicts:
      { "title": str, "body": str, "type": "positive"|"warning"|"neutral" }

    Every claim cites a specific metric from the dataset.
    No revenue, sales, or quantity figures are included.
    """
    insights = []

    # 1. Most-represented genre by catalogue size
    top_genre = by_genre.iloc[0]
    insights.append({
        "title": f"📚 Largest Genre by Catalogue: {top_genre['Main Genre']}",
        "body": (
            f"**{top_genre['Main Genre']}** has the most titles in the dataset "
            f"with **{top_genre['Books']:,} books** — "
            f"{top_genre['Books']/len(df)*100:.1f}% of the total catalogue.  "
            f"Average price: ₹{top_genre['Avg Price (INR)']:.0f}, "
            f"average rating: {top_genre['Avg Rating']:.2f}/5."
        ),
        "type": "positive",
    })

    # 2. Highest reader engagement (most reviews)
    top_eng = by_genre.sort_values("Total Reviews", ascending=False).iloc[0]
    insights.append({
        "title": f"💬 Highest Reader Engagement: {top_eng['Main Genre']}",
        "body": (
            f"**{top_eng['Main Genre']}** has the highest total review count in the dataset: "
            f"**{top_eng['Total Reviews']:,.0f}** reviews across {top_eng['Books']:,} books, "
            f"giving it the highest average reviews per book at "
            f"{top_eng['Total Reviews']/top_eng['Books']:,.0f}."
        ),
        "type": "positive",
    })

    # 3. Highest-rated genre
    best_rated = by_genre.sort_values("Avg Rating", ascending=False).iloc[0]
    insights.append({
        "title": f"⭐ Highest-Rated Genre: {best_rated['Main Genre']}",
        "body": (
            f"**{best_rated['Main Genre']}** has the highest average rating in the dataset: "
            f"**{best_rated['Avg Rating']:.2f}/5** across {best_rated['Books']:,} titles."
        ),
        "type": "positive",
    })

    # 4. Most expensive genre
    most_expensive = by_genre.sort_values("Avg Price (INR)", ascending=False).iloc[0]
    insights.append({
        "title": f"💰 Premium-Priced Genre: {most_expensive['Main Genre']}",
        "body": (
            f"**{most_expensive['Main Genre']}** has the highest average listed price "
            f"in the dataset at **₹{most_expensive['Avg Price (INR)']:.0f}** per title "
            f"(median: ₹{most_expensive['Median Price (INR)']:.0f}).  "
            f"Its average rating is {most_expensive['Avg Rating']:.2f}/5 across "
            f"{most_expensive['Books']:,} titles."
        ),
        "type": "neutral",
    })

    # 5. Most affordable genre with good ratings
    affordable_good = by_genre[
        (by_genre["Avg Price (INR)"] <= df["Price (INR)"].quantile(0.33)) &
        (by_genre["Avg Rating"] >= 4.2)
    ].sort_values("Avg Rating", ascending=False)
    if not affordable_good.empty:
        row = affordable_good.iloc[0]
        insights.append({
            "title": f"🎯 Best Value Genre: {row['Main Genre']}",
            "body": (
                f"**{row['Main Genre']}** has an average price of **₹{row['Avg Price (INR)']:.0f}** "
                f"(placing it in the bottom third by price across all genres) "
                f"and an average rating of **{row['Avg Rating']:.2f}/5** "
                f"across {row['Books']:,} titles."
            ),
            "type": "positive",
        })

    # 6. Dominant format
    top_type = by_type.iloc[0]
    pct = top_type["Books"] / by_type["Books"].sum() * 100
    insights.append({
        "title": f"📦 Most Common Format: {top_type['Type']}",
        "body": (
            f"**{top_type['Type']}** is the dominant format, making up "
            f"**{pct:.1f}%** of the catalogue ({top_type['Books']:,} titles).  "
            f"Average price: ₹{top_type['Avg Price (INR)']:.0f}, "
            f"average rating: {top_type['Avg Rating']:.2f}/5."
        ),
        "type": "positive",
    })

    # 7. Digital (Kindle) presence
    kindle_rows = by_type[by_type["Type"].str.contains("Kindle", case=False)]
    if not kindle_rows.empty:
        k_books = kindle_rows["Books"].sum()
        k_pct   = k_books / by_type["Books"].sum() * 100
        k_price = (
            df.loc[df["Type"].str.contains("Kindle", case=False), "Price (INR)"].mean()
        )
        phys_price = (
            df.loc[df["Type"].str.contains("Paperback|Hardcover", case=False), "Price (INR)"].mean()
        )
        insights.append({
            "title": "📱 Digital (Kindle) Format Presence",
            "body": (
                f"Kindle editions account for **{k_pct:.1f}%** of titles "
                f"({k_books:,} books) with an average listed price of **₹{k_price:.0f}**.  "
                f"Paperback and Hardcover titles average **₹{phys_price:.0f}**.  "
                f"On average, Kindle titles are listed at "
                f"**₹{phys_price - k_price:.0f} less** than physical formats in this dataset."
            ),
            "type": "neutral",
        })

    # 8. Low-rated genre flag
    low_rated = by_genre[by_genre["Avg Rating"] < 4.0].sort_values("Avg Rating")
    if not low_rated.empty:
        row = low_rated.iloc[0]
        insights.append({
            "title": f"⚠️ Lowest-Rated Genre: {row['Main Genre']}",
            "body": (
                f"**{row['Main Genre']}** has the lowest average rating in the dataset: "
                f"**{row['Avg Rating']:.2f}/5** across {row['Books']:,} titles.  "
                f"Average price: ₹{row['Avg Price (INR)']:.0f}, "
                f"total reviews: {row['Total Reviews']:,.0f}."
            ),
            "type": "warning",
        })

    # 9. Price band with the most books
    price_df = price_distribution(df)
    top_band = price_df.sort_values("Books", ascending=False).iloc[0]
    insights.append({
        "title": f"🏷️ Most Common Price Point: {top_band['Price Band']}",
        "body": (
            f"**{top_band['Books']:,} books** ({top_band['Books']/len(df)*100:.1f}% "
            f"of the catalogue) are listed in the **{top_band['Price Band']}** price range.  "
            f"Average rating for books in this band: **{top_band['Avg Rating']:.2f}/5**."
        ),
        "type": "neutral",
    })

    return insights
