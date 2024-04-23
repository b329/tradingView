
import pandas as pd
import numpy as np
import talib

# StochasticRSI Function
# def Stoch(close, high, low, smoothk, smoothd, n):
    # lowestlow = pd.Series.rolling(low, window=n, center=False).min()
    # highesthigh = pd.Series.rolling(high, window=n, center=False).max()
    # K = pd.Series.rolling(100 * ((close - lowestlow) / (highesthigh - lowestlow)), window=smoothk).mean()
    # D = pd.Series.rolling(K, window=smoothd).mean()
    # return K, D

def calculate_moving_averages(df, periods=[5, 10]):
    """이동 평균 계산"""
    for period in periods:
        df[f'MA{period}'] = df['close'].rolling(window=period).mean()
    return df

def calculate_bollinger_bands(df, period=21, bollinger_multiplier=2, increase_threshold=1.03, decrease_threshold=0.97):
    """볼린저 밴드 계산"""
    df['MA20'] = df['close'].rolling(window=period).mean()
    df['std'] = df['close'].rolling(window=period).std()
    df['upper'] = df['MA20'] + (bollinger_multiplier * df['std'])
    df['lower'] = df['MA20'] - (bollinger_multiplier * df['std'])
    df['band_width'] = df['upper'] - df['lower']
    df['band_width_change'] = df['band_width'].ffill().pct_change()
    # 볼린저 밴드 폭 변화에 대한 람다 함수 적용
    df['band_width_increase'] = is_increasing_consecutively(df['band_width'], 3, increase_threshold)
    df['band_width_decrease'] = is_decreasing_consecutively(df['band_width'], 3, decrease_threshold)
    return df

def calculate_band_conditions(df):
    df['buy_middle'] = df['lower'] + (df['MA20'] - df['lower']) * 0.50
    df['sell_middle'] = df['upper'] - (df['upper'] - df['MA20']) * 0.50

    df['close_lower_bands'] = df['close'] < df['lower']
    df['close_upper_bands'] = df['close'] > df['upper']

    df['low_lower_bands'] = df['low'] < df['lower']
    df['high_upper_bands'] = df['high'] > df['upper']

    return df

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """MACD 계산"""
    macd, macdsignal, _ = talib.MACD(df['close'], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
    df['MACD'] = macd
    df['MACD_signal'] = macdsignal
    return df

def calculate_stoch_rsi(df, period=14, smoothk=3, smoothd=3):
    """Stochastic RSI 계산"""
    fastk, fastd = talib.STOCHRSI(df['close'], timeperiod=period, fastk_period=smoothk, fastd_period=smoothd)
    df['stochrsiK'] = fastk
    df['stochrsiD'] = fastd

    return df

def calculate_moving_average_crosses(df, short_period=5, long_period=10):
    """
    이동 평균 골든 크로스와 데드 크로스를 계산합니다.

    Parameters:
    - df: Pandas DataFrame, 주가 데이터를 포함하고 있어야 합니다.
    - short_period: 짧은 기간의 이동 평균을 계산하기 위한 기간입니다.
    - long_period: 긴 기간의 이동 평균을 계산하기 위한 기간입니다.

    Returns:
    - df: 골든 크로스와 데드 크로스가 계산된 DataFrame을 반환합니다.
    """
    # 이동 평균 계산
    df[f'MA{short_period}'] = df['close'].rolling(window=short_period).mean()
    df[f'MA{long_period}'] = df['close'].rolling(window=long_period).mean()

    # 이전 이동 평균 값 계산
    df[f'prev_MA{short_period}'] = df[f'MA{short_period}'].shift(1)
    df[f'prev_MA{long_period}'] = df[f'MA{long_period}'].shift(1)

    # 골든 크로스와 데드 크로스 계산
    df['golden_cross'] = ((df[f'prev_MA{short_period}'] < df[f'prev_MA{long_period}']) &
                          (df[f'MA{short_period}'] > df[f'MA{long_period}']))
    df['dead_cross'] = ((df[f'prev_MA{short_period}'] > df[f'prev_MA{long_period}']) &
                        (df[f'MA{short_period}'] < df[f'MA{long_period}']))

    return df

def calculate_stoch_rsi_crosses(df):
    df['prev_stochrsiK'] = df['stochrsiK'].shift(1)
    df['prev_stochrsiD'] = df['stochrsiD'].shift(1)

    # 골든 크로스: stochrsiK가 stochrsiD를 아래에서 위로 교차
    df['stochrsi_golden_cross'] = ((df['prev_stochrsiK'] < df['prev_stochrsiD']) &
                                   (df['stochrsiK'] > df['stochrsiD']))

    # 데드 크로스: stochrsiK가 stochrsiD를 위에서 아래로 교차
    df['stochrsi_dead_cross'] = ((df['prev_stochrsiK'] > df['prev_stochrsiD']) &
                                 (df['stochrsiK'] < df['stochrsiD']))

    return df

def Stoch(rsi, high, low, smoothK, smoothD, lengthRsi, lengthStoch):
    # RSI 데이터를 사용하여 StochRSI 계산
    # 'lengthStoch'를 기준으로 최고값과 최저값 계산
    stochRsiHigh = rsi.rolling(window=lengthStoch).max()
    stochRsiLow = rsi.rolling(window=lengthStoch).min()

    # StochRSI 계산
    stochRsi = 100 * (rsi - stochRsiLow) / (stochRsiHigh - stochRsiLow)

    # 'smoothK'와 'smoothD'를 사용하여 최종 StochRSI 값 평활화
    stochRsiK = stochRsi.rolling(window=smoothK).mean()
    stochRsiD = stochRsiK.rolling(window=smoothD).mean()

    return stochRsiK, stochRsiD


def is_increasing_consecutively(series, n, threshold=1.03):
    # Check if the condition is True for every element in the Series
    return (series / series.shift(1) > threshold).rolling(window=n).apply(lambda x: x.all(), raw=True)

def is_decreasing_consecutively(series, n, threshold=0.97):
    # Check if the condition is True for every element in the Series
    return (series / series.shift(1) < threshold).rolling(window=n).apply(lambda x: x.all(), raw=True)

# 기존 로직에 새로운 조건을 추가하기 위한 함수 정의
def is_stochrsi_increasing(df, index, periods):
    # stochrsiK와 stochrsiD가 모두 증가하는지 확인
    return all(df.loc[index - periods:index - 1, 'stochrsiK'].diff().dropna() > 0) and \
        all(df.loc[index - periods:index - 1, 'stochrsiD'].diff().dropna() > 0)

def has_golden_cross_occurred(df, index, periods):
    # 주어진 기간 동안 stochrsi_golden_cross가 발생했는지 확인
    return any(df.loc[index - periods:index - 1, 'stochrsi_golden_cross'])

def is_stochrsi_decreasing(df, index, periods):
    # stochrsiK와 stochrsiD가 모두 감소하는지 확인
    return all(df.loc[index-periods:index-1, 'stochrsiK'].diff().dropna() < 0) and \
           all(df.loc[index-periods:index-1, 'stochrsiD'].diff().dropna() < 0)

def has_dead_cross_occurred(df, index, periods):
    # 주어진 기간 동안 stochrsi_dead_cross가 발생했는지 확인
    return any(df.loc[index-periods:index-1, 'stochrsi_dead_cross'])

def get_nearest_1h_stoch_rsi_state(df_15m, df_1h, index):
    current_time = df_15m.loc[index, 'date']
    nearest_index = df_1h.index.get_loc(current_time, method='nearest')
    return df_1h.loc[nearest_index, 'stochrsi_golden_cross'], df_1h.loc[nearest_index, 'stochrsi_dead_cross']


def calculate_volume_change_pct(df):
    """
    데이터프레임 내에서 각 행의 거래량 변화율을 계산하고, 결과를 새로운 컬럼에 저장하는 함수.

    Parameters:
    df (pd.DataFrame): 거래량 변화율을 계산할 pandas 데이터프레임.

    Returns:
    pd.DataFrame: 거래량 변화율 컬럼이 추가된 데이터프레임.
    """
    # 거래량 변화율 계산 (이전 행 대비 현재 행의 거래량 변화율을 백분율로 계산)
    df['volume_change_pct'] = df['volume'].pct_change() * 100

    # NaN 값 처리 (첫 번째 행은 비교 대상이 없으므로 NaN 값이 발생할 수 있음)
    df['volume_change_pct'] = df['volume_change_pct'].fillna(0)

    return df
