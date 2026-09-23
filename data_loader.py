"""
data_loader.py
--------------
Step 1 – Collect & Load the dataset.
Step 2 – Check for missing / incorrect values and clean.

Dataset: Amazon India Best Sellers (scraped catalogue).
Contains: Title, Author, Genre, Sub Genre, Type, Price, Rating,
          No. of People Rated, URL.

NOTE: This dataset does NOT contain quantity sold or revenue figures.
All analysis is limited to price, ratings, review counts, genre, and format.
"""

import numpy as np
import pandas as pd

# ── file paths ────────────────────────────────────────────────────────────────
BOOKS_PATH    = "Dataset/Amazon_Books_Scraping/Books_df.csv"
GENRE_PATH    = "Dataset/Amazon_Books_Scraping/Genre_df.csv"
SUBGENRE_PATH = "Dataset/Amazon_Books_Scraping/Sub_Genre_df.csv"


# ── helpers ───────────────────────────────────────────────────────────────────

def _clean_price(series: pd.Series) -> pd.Series:
    """Strip the ₹ currency symbol and convert to float."""
    return (
        series.astype(str)
              .str.replace(r"[₹,\s]", "", regex=True)
              .pipe(pd.to_numeric, errors="coerce")
    )


# ── public API ────────────────────────────────────────────────────────────────

def load_raw() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return the three raw DataFrames exactly as read from disk."""
    books     = pd.read_csv(BOOKS_PATH,    index_col=0)
    genres    = pd.read_csv(GENRE_PATH)
    subgenres = pd.read_csv(SUBGENRE_PATH)
    return books, genres, subgenres


def load_clean() -> pd.DataFrame:
    """
    Full pipeline: load → clean → return analysis-ready DataFrame.

    Cleaning steps applied:
      - Fill 21 missing Author values with 'Unknown'
      - Parse Price string to numeric float (drop unparseable rows)
      - Drop rows where Rating is outside 0–5
      - Drop rows where review count is zero or negative
      - Drop exact duplicates on (Title, Author, Type)
    """
    books, _, _ = load_raw()

    # ── missing values ────────────────────────────────────────────────────────
    books["Author"] = books["Author"].fillna("Unknown")

    # ── price: strip symbol, coerce to float ──────────────────────────────────
    books["Price (INR)"] = _clean_price(books["Price"])
    before = len(books)
    books = books.dropna(subset=["Price (INR)"])
    dropped_price = before - len(books)

    # ── rating: must be 0–5 ───────────────────────────────────────────────────
    books.loc[~books["Rating"].between(0, 5), "Rating"] = np.nan
    before = len(books)
    books = books.dropna(subset=["Rating"])
    dropped_rating = before - len(books)

    # ── review count: must be positive ───────────────────────────────────────
    books.loc[books["No. of People rated"] <= 0, "No. of People rated"] = np.nan
    before = len(books)
    books = books.dropna(subset=["No. of People rated"])
    dropped_reviews = before - len(books)

    # ── duplicates ────────────────────────────────────────────────────────────
    before = len(books)
    books = books.drop_duplicates(subset=["Title", "Author", "Type"])
    dropped_dupes = before - len(books)

    # ── store audit metadata ──────────────────────────────────────────────────
    books.attrs["audit"] = {
        "dropped_price":   dropped_price,
        "dropped_rating":  dropped_rating,
        "dropped_reviews": dropped_reviews,
        "dropped_dupes":   dropped_dupes,
        "final_rows":      len(books),
    }

    # ── tidy column names ─────────────────────────────────────────────────────
    books = books.rename(columns={"No. of People rated": "Review Count"})

    return books.reset_index(drop=True)
