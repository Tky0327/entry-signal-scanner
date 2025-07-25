import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, start="2023-01-01", end=None, interval="1d"):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end, interval=interval)
    return df

def calculate_indicators(df):
    df['High-Low'] = df['High'] - df['Low']
    df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    df['EMA30'] = df['Close'].ewm(span=30).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df['SMA10'] = df['Close'].rolling(window=10).mean()
    df['Prev_Close'] = df['Close'].shift(1)
    df['Prev_Volume'] = df['Volume'].shift(1)
    return df

def confirm_uptrend(df, window=10):
    return ((df['Close'] > df['SMA10']).rolling(window).sum() == window) & \
           (df['SMA10'].diff(window) > 0)

def confirm_pullback(df):
    return df['Close'] < df['SMA10']

def confirm_consolidation(df, window=5, atr_multiplier=1, min_days=3):
    lower = df['EMA30'] - df['ATR'] * atr_multiplier
    upper = df['EMA30'] + df['ATR'] * atr_multiplier
    within_band = ((df['Close'] >= lower) & (df['Close'] <= upper))
    return within_band.rolling(window).sum() >= min_days

def confirm_breakout(df):
    return (
        (df['Close'] > df['SMA10']) &
        (df['SMA10'] > df['EMA30']) &
        (df['EMA30'] > df['EMA50']) &
        (df['EMA50'] > df['EMA200']) &
        (df['Volume'] > df['Prev_Volume'])&
        (df['Close'] > df['Prev_Close'])
    )

def confirm_invalid_consolidation(df):
    return df['Close'] < 0.97 * df['EMA30']

def add_stepwise_entry_signal(df):
    state = 0
    entry_signal = []

    for i in range(len(df)):
        row = df.iloc[i]

        if row['Confirm_InvalidConsolidation'] == 1:
            state = 0
            entry_signal.append(0)
            continue

        if (
            row['Confirm_Uptrend'] == 0 and
            row['Confirm_Pullback'] == 0 and
            row['Confirm_Consolidation'] == 0 and
            row['Confirm_Breakout'] == 0
        ):
            state = 0
            entry_signal.append(0)
            continue

        if state == 0 and row['Confirm_Uptrend'] == 1:
            state = 1
        elif state == 1 and row['Confirm_Pullback'] == 1:
            state = 2
        elif state == 2 and row['Confirm_Consolidation'] == 1:
            state = 3
        elif state == 3 and row['Confirm_Breakout'] == 1:
            entry_signal.append(1)
            state = 0
            continue

        entry_signal.append(0)

    return pd.Series(entry_signal, index=df.index)

def add_all_confirmation_columns(df):
    df = calculate_indicators(df)
    df['Confirm_Uptrend'] = confirm_uptrend(df).astype(int)
    df['Confirm_Pullback'] = confirm_pullback(df).astype(int)
    df['Confirm_Consolidation'] = confirm_consolidation(df).astype(int)
    df['Confirm_Breakout'] = confirm_breakout(df).astype(int)
    df['Confirm_InvalidConsolidation'] = confirm_invalid_consolidation(df).astype(int)
    df['Entry_Signal'] = add_stepwise_entry_signal(df)
    return df
