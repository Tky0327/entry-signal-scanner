import pandas as pd
import json
from signal_logic import fetch_stock_data, add_all_confirmation_columns
import subprocess
import os

TICKER_FILE = r"C:\Users\OEM\Documents\Jack\unique_tickers.csv"
OUTPUT_FILE = r"C:\Users\OEM\Documents\Jack\signal_results.json"
DAYS_LOOKBACK = 5

def main():
    tickers_df = pd.read_csv(TICKER_FILE)
    tickers = tickers_df['ticker'].dropna().unique().tolist()

    signal_by_date = {}

    for ticker in tickers:
        try:
            df = fetch_stock_data(ticker)
            df = add_all_confirmation_columns(df)
            recent = df.tail(DAYS_LOOKBACK)

            for idx, row in recent.iterrows():
                if row['Entry_Signal'] == 1:
                    signal_date = idx.strftime('%Y-%m-%d')
                    signal_by_date.setdefault(signal_date, []).append(ticker)
        except Exception as e:
            print(f"Error with {ticker}: {e}")

    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(signal_by_date, f, indent=2)
    print(f"✅ Signal data saved to {OUTPUT_FILE}")

    REPO_PATH = r"C:\Users\OEM\Documents\Jack"  # path to your repo folder

    os.chdir(REPO_PATH)
    subprocess.run(["git", "add", "signal_results.json"])
    subprocess.run(["git", "commit", "-m", "🕒 Auto update signal results"])
    subprocess.run(["git", "push"])


if __name__ == "__main__":
    main()
