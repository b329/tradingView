import logging
import os
import time

from binance.client import Client
import pprint
import pandas as pd  # needs pip install
import numpy as np
import talib as ta
import matplotlib.pyplot as plt  # needs pip install
from binance.error import ClientError


def get_data_frame():
    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    # request historical candle (or klines) data using timestamp from above, interval either every min, hr, day or month
    # starttime = '30 minutes ago UTC' for last 30 mins time
    starttime = '5 day ago UTC'
    # interval = '1m'
    interval = '3m'
    bars = client.get_historical_klines(symbol, interval, starttime)

    for line in bars:  # Keep only first 5 columns, "date" "open" "high" "low" "close"
        del line[5:]

    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])

    return df


def plot_bollinger_bands_macd_rsi_adx_graph(df):
    df = df.astype(float)
    # 예를 들어, (20, 10)으로 수정하면 그림의 가로는 20인치, 세로는 10인치로 출력됩니다.
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(df.index, df['close'], label='Close', linewidth=0.5)
    ax.plot(df.index, df['MA20'], label='SMA', linewidth=0.5)
    ax.plot(df.index, df['upper'], label='Upper Band', linewidth=0.5)
    ax.plot(df.index, df['lower'], label='Lower Band', linewidth=0.5)
    ax.fill_between(df.index, df['lower'], df['upper'], color='grey', alpha=0.30)

    # 이동 평균선 추가된 부분
    ax.plot(df.index, df['MA5'], label='MA5', linewidth=0.5)
    ax.plot(df.index, df['MA10'], label='MA10', linewidth=0.5)

    ax.set_xlabel('Date', fontsize=18)
    ax.set_ylabel('Close price', fontsize=18)
    ax.legend(loc='upper left')


def trade_logic():
    symbol_df = get_data_frame()

    # Calculate 5-day and 10-day Moving Averages
    period_short = 5
    period_long = 10
    symbol_df['MA5'] = symbol_df['close'].rolling(period_short).mean()
    symbol_df['MA10'] = symbol_df['close'].rolling(period_long).mean()

    # Calculate Golden and Dead Cross for 5-day and 10-day Moving Averages
    symbol_df['prev_MA5'] = symbol_df['MA5'].shift(1)
    symbol_df['prev_MA10'] = symbol_df['MA10'].shift(1)
    symbol_df['golden_cross'] = (symbol_df['prev_MA5'] < symbol_df['prev_MA10']) & (
                symbol_df['MA5'] > symbol_df['MA10'])
    symbol_df['dead_cross'] = (symbol_df['prev_MA5'] > symbol_df['prev_MA10']) & (symbol_df['MA5'] < symbol_df['MA10'])

    # 스토캐스틱
    # Calculate Stochastic Oscillator
    # symbol_df['stoch_position']은 스토캐스틱의 현재 위치를 나타내는 열입니다. 0, 1 또는 -1 중 하나의 값을 가질 수 있습니다.
    #
    # 0: 스토캐스틱이 오버바우트나 오버셀드 지역에 위치하지 않는 경우
    # 1: 스토캐스틱이 오버셀드 지역에 위치하는 경우 (스토캐스틱이 20 이하인 경우)
    # -1: 스토캐스틱이 오버바우트 지역에 위치하는 경우 (스토캐스틱이 80 이상인 경우)
    # symbol_df['stoch_position']의 값이 0인 경우는 현재 가격이 이전 주가의 상승과 하락을 반복하며 횡보하는 상태를 나타냅니다.
    # 1인 경우는 현재 가격이 일정 기간 동안의 주가 변동폭에서 하락한 상태를 나타내며, 이는 과매도 상태를 의미합니다.
    # 반대로, -1인 경우는 현재 가격이 일정 기간 동안의 주가 변동폭에서 상승한 상태를 나타내며, 이는 과매수 상태를 의미합니다.

    # Calculate Bollinger Bands
    period = 14
    symbol_df['MA20'] = symbol_df['close'].rolling(period).mean()
    symbol_df['std'] = symbol_df['close'].rolling(period).std()
    symbol_df['upper'] = symbol_df['MA20'] + (2 * symbol_df['std'])
    symbol_df['lower'] = symbol_df['MA20'] - (2 * symbol_df['std'])
    # Calculate Bollinger Band Width
    symbol_df['band_width'] = symbol_df['upper'] - symbol_df['lower']
    # Get current prices
    current_price = client.get_symbol_ticker(symbol=symbol)


    # 체크 필요. 거래 많음.

    symbol_df['buy'] = (symbol_df['MA5'] > symbol_df['MA10']) \
                       & (symbol_df['slowk'] > symbol_df['slowd']) \
                       & (symbol_df['MACD'] > symbol_df['signal_macd']) \
                       & (symbol_df['ADX'] > 20)

    symbol_df['sell'] = (symbol_df['MA5'] < symbol_df['MA10']) \
                        & (symbol_df['slowk'] < symbol_df['slowd']) \
                        & (symbol_df['MACD'] < symbol_df['signal_macd']) \
                        & (symbol_df['ADX'] > 20)

    symbol_df['buy'] = (symbol_df['golden_cross'] == True)

    symbol_df['sell'] = (symbol_df['dead_cross'] == True)

    # 초기값 설정
    # Check if the current price satisfies the conditions for MACD and Bollinger Bands
    # 위 예시에서는 sri_buy와 sri_sell이라는 새로운 컬럼을 추가하여, SRI 기준에 따라 매수/매도 시그널을 계산하였습니다.
    # 또한, 현재 가격이 상단/하단 밴드 기준을 넘었는지 확인하는 부분에서도 SRI 기준을 추가하여 BUY/SELL/HOLD 시그널을 출력하였습니다.

    with open('output_bollinger_macd_rsi_bands.csv', 'w') as f:
        f.write(
            symbol_df.to_string()
        )

    # 이 함수는 주가 데이터프레임에서 Bollinger Bands와 함께 주가 차트를 그리고,
    # 매수와 매도 지점을 나타내는 마커를 추가합니다. x, y 축 레이블과 범례도 함께 추가되어 있습니다.
    plot_bollinger_bands_macd_rsi_adx_graph(symbol_df)


def main():
    trade_logic()


while True:
    if __name__ == "__main__":
        api_key = os.environ.get('BINANCE_TESTNET_KEY')  # passkey (saved in bashrc for linux)
        api_secret = os.environ.get('BINANCE_TESTNET_PASSWORD')  # secret (saved in bashrc for linux)
        # client = Client(api_key, api_secret, testnet=True)
        client = Client(api_key, api_secret)
        print("Using Bot")

        # pprint.pprint(client.get_account())

        symbol = 'BTCUSDT'  # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC

        main()

        time.sleep(600)  # 10초마다 코드가 실행됩니다.
