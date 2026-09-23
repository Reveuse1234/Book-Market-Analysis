# Project Report: Book Market Analysis

**Programme:** AICTE + IBM Internship — Data Analytics  
**Dataset:** Amazon India Books Best Sellers (scraped catalogue)  
**Tools:** Python 3, Pandas, NumPy, Plotly, Streamlit  
**Repository files:** `data_loader.py` · `analysis.py` · `app.py`

---

## Abstract

This project performs an exploratory data analysis (EDA) of a scraped Amazon
India book catalogue containing 7,928 listings across 30 genres and 33 format
types. After data cleaning, 5,633 records are retained. The analysis examines
catalogue distribution by genre and format, listed prices, reader ratings, and
review counts. An interactive three-page Streamlit dashboard presents the
findings through 12 Plotly charts, nine data-backed insights, and live sidebar
filters. The dataset does not contain sales volumes or revenue figures; all
analysis is limited to the fields that are directly present.

---

## 1. Introduction

Online book retail platforms publish large catalogues of titles across diverse
genres and formats. Publicly available scraping of Amazon India's Best Sellers
pages yields a rich snapshot of the catalogue: what is listed, how it is
priced, how readers have rated it, and how many reviews each title has
accumulated. This data can be used to understand the structure of the listed
book market — which genres are most represented, how prices vary across formats
and genres, and which titles or genres attract the most reader reviews.

This project builds an end-to-end analytics pipeline:

1. Load and validate the raw scraped data.
2. Clean and standardise it.
3. Compute grouped summaries and descriptive statistics.
4. Visualise the results with interactive charts.
5. Derive factual, data-backed observations presented as dashboard insights.

---

## 2. Problem Statement

Given a scraped catalogue of Amazon India book listings, answer the following
descriptive questions using only the data that is present:

- How are books distributed across genres and formats?
- How do listed prices vary across genres and format types?
- How do average reader ratings compare across genres?
- Which titles have accumulated the most reviews?
- Which price bands contain the most titles, and how do ratings vary by band?
- Are there observable differences in listed prices between digital (Kindle)
  and physical (Paperback, Hardcover) formats?

No sales volumes, units sold, or revenue figures are available in the dataset.
The project does not estimate, simulate, or infer any such figures.

---

## 3. Objectives

1. Load and inspect the three raw CSV files from the dataset archive.
2. Identify and handle data quality issues (missing values, invalid ranges,
   duplicate records, non-numeric price strings).
3. Compute descriptive statistics and grouped aggregations for genres, formats,
   price bands, and rating bands.
4. Build 12 interactive Plotly charts covering catalogue distribution, pricing,
   ratings, review counts, and format comparisons.
5. Derive nine factual insights, each grounded in a specific measured value
   from the dataset with no causal claims or unsupported explanations.
6. Present all findings in a three-page Streamlit dashboard with sidebar
   filters that allow users to narrow the analysis by genre, format, price
   range, and rating range.

---

## 4. Dataset Description

### 4.1 Source

The dataset is a scraped snapshot of Amazon India's Books Best Sellers pages,
distributed as `archive(dataset).zip`. It contains three CSV files located
under `Amazon_Books_Scraping/`.

### 4.2 Files

| File | Rows | Description |
|---|---|---|
| `Books_df.csv` | 7,928 | Primary listing data — one row per book |
| `Genre_df.csv` | 35 | Top-level genre names and Amazon URLs |
| `Sub_Genre_df.csv` | 329 | Sub-genres linked to parent genres |

### 4.3 Fields in Books_df.csv

| Column | Raw Type | Description |
|---|---|---|
| Title | string | Book title as listed on Amazon |
| Author | string | Author name; 21 records missing |
| Main Genre | string | Top-level genre; 30 distinct values |
| Sub Genre | string | Sub-category; 151 distinct values |
| Type | string | Format (Paperback, Kindle Edition, Hardcover, etc.); 33 distinct values |
| Price | string | Listed price in INR, e.g. `₹329.00`; requires parsing |
| Rating | float | Average star rating on a 0–5 scale |
| No. of People rated | float | Count of reviews on the Amazon listing |
| URLs | string | Direct Amazon listing URL |

### 4.4 What the dataset does NOT contain

- Quantity sold
- Units sold
- Revenue or sales figures of any kind
- Publisher information
- Publication date
- ISBN

The `No. of People rated` column records how many Amazon reviewers have left
a rating for that listing. It is **not** equivalent to the number of copies
sold; Amazon reviews are voluntary and represent only a subset of purchasers.

---

## 5. Data Cleaning and Preprocessing

All cleaning is implemented in `data_loader.load_clean()` and produces an
audit record stored in `df.attrs["audit"]` for display in the dashboard.

### 5.1 Steps applied

| # | Issue | Detection | Action | Rows affected |
|---|---|---|---|---|
| 1 | Missing `Author` values | `df["Author"].isna()` | Fill with string `"Unknown"` | 21 |
| 2 | `Price` is a string (e.g. `₹329.00`) | dtype = object | Strip `₹` and `,`, coerce to float via `pd.to_numeric(errors="coerce")`; drop rows where result is NaN | 0 dropped |
| 3 | `Rating` outside valid range 0–5 | `~rating.between(0, 5)` | Set to NaN, then drop | 0 dropped |
| 4 | `No. of People rated` ≤ 0 | value ≤ 0 | Set to NaN, then drop | 306 dropped |
| 5 | Exact duplicate listings | `duplicated(["Title","Author","Type"])` | Keep first occurrence, drop rest | 1,989 dropped |

### 5.2 Result

| Metric | Value |
|---|---|
| Raw rows | 7,928 |
| Rows removed | 2,295 |
| **Clean rows** | **5,633** |
| Clean columns used | 10 |

### 5.3 Column names after cleaning

| Column | Type | Notes |
|---|---|---|
| Title | string | Unchanged |
| Author | string | NaNs filled with "Unknown" |
| Main Genre | string | Unchanged |
| Sub Genre | string | Unchanged |
| Type | string | Unchanged |
| Price (INR) | float | Parsed from raw Price string |
| Rating | float | Validated 0–5 |
| Review Count | float | Renamed from "No. of People rated" |
| URLs | string | Unchanged |
| Price | string | Original column retained (not used in analysis) |

---

## 6. Exploratory Data Analysis

All EDA is performed in `analysis.py`. The following summary tables are
computed:

### 6.1 Overall dataset statistics

| Metric | Value |
|---|---|
| Total books (clean) | 5,633 |
| Unique genres | 30 |
| Unique sub-genres | 151 |
| Unique authors | 3,519 |
| Average listed price | ₹519 |
| Median listed price | ₹329 |
| Average rating | 4.43 / 5 |
| Total reviews | ~30.9 million |

### 6.2 Per-genre summary (`summary_by_genre`)

Computed fields per genre: book count, average price (INR), median price (INR),
average rating, total review count, average reviews per book.
Sorted by book count descending.

Top 5 genres by catalogue size:

| Genre | Books | Avg Price (₹) | Avg Rating | Total Reviews |
|---|---|---|---|---|
| Children's Books | 883 | 295 | 4.52 | 5,086,240 |
| Romance | 849 | 328 | 4.33 | 5,643,799 |
| Sports | 544 | 658 | 4.38 | 1,195,579 |
| Literature & Fiction | 400 | 504 | 4.52 | 3,276,510 |
| Teen & Young Adult | 350 | 349 | 4.46 | 1,902,154 |

### 6.3 Per-format summary (`summary_by_type`)

Computed fields per format: book count, average price (INR), average rating,
total review count. Sorted by book count descending.

Top 5 formats by catalogue size:

| Format | Books | Avg Price (₹) | Avg Rating | Total Reviews |
|---|---|---|---|---|
| Paperback | 2,992 | 533 | 4.44 | 16,421,804 |
| Kindle Edition | 1,693 | 319 | 4.35 | 9,398,137 |
| Hardcover | 539 | 1,008 | 4.54 | 1,419,627 |
| Audible Audiobook | 151 | 850 | 4.54 | 854,897 |
| Board book | 99 | 263 | 4.58 | 328,073 |

### 6.4 Price distribution

Books are binned into seven price bands:

| Band | Books | Avg Rating |
|---|---|---|
| ₹0–100 | 247 | 4.35 |
| ₹101–200 | 726 | 4.42 |
| ₹201–300 | 893 | 4.43 |
| ₹301–500 | 1,734 | 4.45 |
| ₹501–800 | 898 | 4.41 |
| ₹801–1200 | 579 | 4.43 |
| ₹1200+ | 556 | 4.41 |

The ₹301–500 band contains the most titles (1,734; 30.8% of the catalogue).

### 6.5 Rating distribution

The vast majority of books are rated between 4.0 and 5.0. Fewer than 5% of
titles have an average rating below 4.0. The overall average is 4.43/5.

---

## 7. Analysis Methodology

The project uses purely descriptive statistics. No inferential tests,
predictive models, or machine learning are applied.

**Grouping:** `pandas.groupby` with named aggregations (`count`, `mean`,
`median`, `sum`).

**Binning:** `pandas.cut` for price bands and rating brackets with fixed,
domain-meaningful bin edges.

**Normalisation (heatmap only):** Min-max normalisation per column to enable
visual comparison of metrics with different scales. The raw values are shown
separately in the genre summary table.

**Filtering:** All summary tables, charts, and insights recompute on the
filtered DataFrame whenever sidebar filters are changed. Streamlit's
`@st.cache_data` caches the initial full-dataset computation.

---

## 8. Dashboard Design

The Streamlit application (`app.py`) is structured as a single-file app with
three pages selected via a sidebar radio widget. A second sidebar section
provides four filters: genre (multi-select), format (multi-select), price
range (range slider), and rating range (range slider). All filters apply to
every chart and table on the active page.

### Page 1 — Market Overview

Purpose: give a high-level picture of what the dataset contains.

| Element | Description |
|---|---|
| Dataset disclaimer | Clearly states this is a scraped catalogue with no sales data |
| 8 KPI cards | Total books, genres, sub-genres, authors, avg/median price, avg rating, total reviews |
| Data quality badges | Shows the 5 cleaning steps and rows affected |
| Catalogue by Genre (bar) | Book count per genre, horizontal |
| Catalogue Share (donut) | % share for the top 12 genres |
| Total Reviews by Genre (bar) | Sum of review counts per genre, horizontal |
| Rating Distribution (histogram) | Distribution of average ratings across all books |
| Books per Price Band (bar) | Count of books in each price band, coloured by avg rating |

### Page 2 — Book & Genre Analysis

Purpose: allow detailed comparison across genres, formats, and individual books.

| Element | Description |
|---|---|
| 4 price metric cards | Min, avg, median, max listed price |
| Avg Price by Genre (bar) | Mean price per genre |
| Avg Price by Format (bar) | Mean price per format type |
| Price vs Rating scatter | Bubble scatter: x=price, y=rating, size=review count, colour=genre |
| 4 rating metric cards | Avg, median, books ≥ 4.5, books < 3.5 |
| Avg Rating by Genre (bar) | Mean rating per genre |
| Rating Brackets (bar) | Count of books in each 0.5-point rating band |
| Catalogue Share by Format (donut) | % of books per format |
| Price & Rating by Format (dual-axis) | Bar for avg price + line for avg rating |
| Most-Reviewed Books (bar) | Top N books by review count, slider 5–30 |
| Highest-Rated Books (table) | Top N books by avg rating, min 500 reviews |
| Genre Comparison Heatmap | Normalised values for books, price, rating, reviews per genre |
| Genre Summary Table | Full genre aggregation table with formatted values |

### Page 3 — Insights

Purpose: surface structured, readable observations supported by specific numbers.

| Element | Description |
|---|---|
| 7–9 insight cards | Colour-coded: green (positive), orange (warning), blue (neutral) |
| 4 supporting charts | Avg Rating by Genre, Avg Price by Genre, Total Reviews by Genre, Price Band bar |
| Raw Data Explorer | Searchable table of all filtered records |

---

## 9. Visualisations

All 12 chart functions are defined in `analysis.py` and rendered with
`st.plotly_chart(fig, use_container_width=True)`.

| # | Function | Chart type | X / Y or Values |
|---|---|---|---|
| 1 | `fig_books_by_genre` | Horizontal bar | Books per genre |
| 2 | `fig_books_by_genre_pie` | Donut | Catalogue % per genre (top 12) |
| 3 | `fig_avg_price_by_genre` | Vertical bar | Avg price per genre |
| 4 | `fig_avg_rating_by_genre` | Vertical bar | Avg rating per genre |
| 5 | `fig_books_by_type` | Donut | Catalogue % per format (top 8 + Other) |
| 6 | `fig_top_by_reviews` | Horizontal bar | Review count per book, coloured by rating |
| 7 | `fig_price_distribution` | Vertical bar | Books per price band, coloured by avg rating |
| 8 | `fig_rating_distribution` | Histogram | Distribution of avg ratings |
| 9 | `fig_price_vs_rating` | Bubble scatter | Price vs rating, sized by review count |
| 10 | `fig_reviews_by_genre` | Horizontal bar | Total reviews per genre |
| 11 | `fig_price_by_type` | Vertical bar | Avg price per format |
| 12 | `fig_genre_heatmap` | Heatmap | Normalised books / price / rating / reviews per genre |

---

## 10. Key Findings

The following findings are derived directly from the clean dataset. They
describe observed patterns; they do not claim causation or imply external
market conditions.

1. **Children's Books** is the largest genre in this catalogue with 883 titles
   (15.7% of the clean dataset), followed by Romance (849 titles) and Sports
   (544 titles).

2. **Romance** has the highest total review count at 5,643,799, and the highest
   average reviews per book of the major genres (6,648 per title).

3. **Biographies, Diaries & True Accounts** has the highest average rating
   in the dataset at approximately 4.56/5.

4. **Medicine & Health Sciences** has the highest average listed price.
   Hardcover is the most expensive format on average at ₹1,008 per title.

5. **Kindle Edition** titles average ₹319, compared to ₹533 for Paperback and
   ₹1,008 for Hardcover — a difference of ₹214 and ₹689 respectively. The
   dataset does not explain why prices differ between formats.

6. **Paperback** is the most common format: 2,992 titles (53.1% of the
   catalogue). Kindle Edition is second with 1,693 titles (30.1%).

7. The **₹301–500** price band contains the most titles: 1,734 books (30.8%
   of the catalogue) with an average rating of 4.45/5.

8. Ratings are concentrated in the 4.0–4.5 range across all genres. Fewer
   than 5% of titles in the dataset average below 4.0.

9. The most-reviewed single title is *Where the Crawdads Sing* with 500,119
   reviews in this dataset. High review counts reflect reader activity on
   the Amazon platform, not units sold.

---

## 11. Limitations

1. **No sales data.** The dataset contains listed prices and review counts.
   It does not contain quantity sold, revenue, or purchase figures. Review
   counts cannot be treated as a proxy for sales.

2. **Point-in-time snapshot.** The data was scraped at a specific date.
   Prices, ratings, and review counts on Amazon change over time. The dataset
   may not reflect current listings.

3. **Best Sellers bias.** The data was scraped from Amazon India's Best Sellers
   pages. It does not represent all books available on Amazon, and it does not
   represent the broader book market outside Amazon India.

4. **Price is listed price only.** Actual transaction prices may differ due to
   discounts, promotions, or third-party sellers. The scraped price is the
   displayed listing price only.

5. **Review count ≠ sales.** Amazon reviews are voluntary. Many purchasers
   do not leave reviews. Genres or titles with fewer reviews are not
   necessarily less commercially active.

6. **Ratings reflect Amazon's review system.** The average rating is shaped by
   who chooses to review, potential review incentives, and the Amazon platform's
   own policies — not solely by the intrinsic quality of the content.

7. **Author field quality.** 21 author records were missing and filled with
   "Unknown". Some titles may have multiple authors or editors listed
   inconsistently across rows.

---

## 12. Conclusion

This project demonstrates a complete data analytics workflow applied to a
real-world scraped dataset. Using Python, Pandas, Plotly, and Streamlit, the
project loads, cleans, analyses, and visualises 5,633 Amazon India book
catalogue records across 30 genres and 33 format types.

The dashboard provides accurate, descriptive insights about catalogue
distribution, pricing patterns, rating distributions, and review engagement —
all grounded in the fields that are actually present in the dataset. No sales
figures, revenue estimates, or demand assumptions are introduced.

The project illustrates how to work honestly with a dataset that has
inherent limitations: acknowledging what data is absent, avoiding unsupported
causal claims, and communicating findings in plain, factually grounded language.

---

## 13. Future Scope

The following extensions could improve the analysis if additional data becomes
available:

1. **Time-series scraping.** Collecting the same listings at multiple points
   in time would allow tracking of price changes and rating trends.

2. **Cross-platform comparison.** Scraping equivalent data from Flipkart or
   other retailers would allow platform-level price and rating comparisons.

3. **Publisher data.** Adding publisher information would enable analysis of
   catalogue composition by publisher.

4. **Actual sales data.** If sales data were available (e.g. from a publisher
   or retailer), the existing price and rating features could be used as inputs
   for predictive modelling of sales volume.

5. **Text analysis.** Applying NLP to book titles, descriptions, or review text
   could surface topic trends or sentiment patterns within genres.

6. **ISBN linkage.** Linking records to a bibliographic database via ISBN would
   resolve duplicate titles across formats and provide publication dates.

---

## 14. File Reference

| File | Purpose |
|---|---|
| `data_loader.py` | Loads raw CSVs; cleans and returns analysis-ready DataFrame via `load_clean()`; raw access via `load_raw()` |
| `analysis.py` | `summary_overall()`, `summary_by_genre()`, `summary_by_type()`, `top_books_by_reviews()`, `top_books_by_rating()`, `price_distribution()`, `rating_bins()`, 12 Plotly chart functions, `market_insights()` |
| `app.py` | 3-page Streamlit dashboard with sidebar filters; all summaries and insights recompute dynamically on filtered data |
| `requirements.txt` | `streamlit>=1.32.0`, `pandas>=2.0.0`, `numpy>=1.24.0`, `plotly>=5.18.0` |
| `README.md` | Setup instructions, dataset summary, page descriptions, cleaning table |
| `PROJECT_REPORT.md` | This document |
| `Dataset/Amazon_Books_Scraping/` | Extracted CSV files from `archive(dataset).zip` |
