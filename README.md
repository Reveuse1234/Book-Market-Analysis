# Book Market Analysis

An interactive data analytics dashboard for analysing the **Amazon India Books Best Sellers** catalogue.

---

## Dataset

**Source:** `archive(dataset).zip` → `Amazon_Books_Scraping/`

| File | Contents |
|---|---|
| `Books_df.csv` | 7,928 scraped book listings |
| `Genre_df.csv` | 35 top-level genres |
| `Sub_Genre_df.csv` | 329 sub-genres |

**Available fields per book:**

- Title, Author
- Main Genre, Sub Genre
- Type (Paperback, Kindle Edition, Hardcover, …)
- Price (listed price in INR, as scraped)
- Rating (0–5 star average)
- No. of People Rated (total review count)
- URL

> ⚠️ **Important:** This dataset contains scraped catalogue and listing data only.
> It does **not** contain quantity sold, revenue, or any sales figures.
> All analysis is limited to price, rating, review count, genre, and format.

---

## Project Structure

```
.
├── app.py            # Streamlit dashboard (3 pages)
├── analysis.py       # Summaries, Plotly charts, and insights
├── data_loader.py    # Data loading and cleaning pipeline
├── requirements.txt  # Python dependencies
├── README.md
├── PROJECT_REPORT.md
└── Dataset/
    └── Amazon_Books_Scraping/
        ├── Books_df.csv
        ├── Genre_df.csv
        └── Sub_Genre_df.csv
```

---

## Setup & Run

```bash
# 1. Extract the dataset (only needed once)
unzip "archive(dataset).zip" -d Dataset/

# 2. Install dependencies
python3 -m pip install -r requirements.txt

# 3. Launch the dashboard
python3 -m streamlit run app.py
```

---

## Dashboard Pages

| Page | What it shows |
|---|---|
| **Market Overview** | KPIs, data quality summary, catalogue size by genre, total reviews by genre, rating distribution, price band distribution |
| **Book & Genre Analysis** | Pricing stats and charts, rating breakdown, format comparison, most-reviewed books, highest-rated books, genre heatmap, genre summary table |
| **Insights** | Data-backed observations on genre size, review counts, ratings, pricing, and format distribution |

All pages support live sidebar filters for genre, format, price range, and rating range.

---

## Data Cleaning Steps

| Issue | Action | Rows affected |
|---|---|---|
| Missing `Author` | Filled with `"Unknown"` | 21 |
| Non-numeric `Price` | Rows dropped | 0 |
| `Rating` outside 0–5 | Rows dropped | 0 |
| `Review Count` ≤ 0 | Rows dropped | 306 |
| Duplicate (Title + Author + Type) | First kept, rest dropped | 1,989 |

**Clean dataset: 5,633 rows.**

---

## Dependencies

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
```
