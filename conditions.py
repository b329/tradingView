# check buy logic
def check_bollinger_band_width(df, index, threshold):
    band_width = df.loc[index, 'band_width']
    return band_width >= threshold

def check_price_above_ma(df, index, ma_column='MA20'):
    close_price = df.loc[index, 'close']
    ma_price = df.loc[index, ma_column]
    return close_price > ma_price

def check_golden_cross(df, index):
    return df.loc[index, 'golden_cross']

def check_volume_above_ma(df, index, ma_column='MA5'):
    volume = df.loc[index, 'volume']
    ma_volume = df.loc[index, ma_column]
    return volume > ma_volume

def check_stochrsi_increasing(df, index, periods):
    if index < periods:  # 충분한 데이터가 없는 경우 False 반환
        return False

    increasing_k = True
    increasing_d = True

    for i in range(index-periods+1, index+1):
        if i == 0:  # 첫 번째 인덱스는 비교할 이전 값이 없으므로 건너뜀
            continue

        # stochrsiK 값이 증가하는지 확인
        if df.loc[i, 'stochrsiK'] <= df.loc[i-1, 'stochrsiK']:
            increasing_k = False

        # stochrsiD 값이 증가하는지 확인
        if df.loc[i, 'stochrsiD'] <= df.loc[i-1, 'stochrsiD']:
            increasing_d = False

    return increasing_k and increasing_d

# conditions.py

def check_stochastic_golden_cross(df, index):
    # 주어진 인덱스에서 Stochastic RSI Golden Cross가 발생했는지 확인합니다.
    if index == 0:
        return False  # 첫 번째 인덱스에서는 비교할 이전 값이 없습니다.

    # 'stochrsiK'와 'stochrsiD'를 사용
    current_k = df.loc[index, 'stochrsiK']
    current_d = df.loc[index, 'stochrsiD']
    prev_k = df.loc[index-1, 'stochrsiK']
    prev_d = df.loc[index-1, 'stochrsiD']

    # Golden Cross 조건: 이전 K가 D 아래였다가 현재 K가 D 위로 교차
    return prev_k < prev_d and current_k > current_d

# check sell point logic
def check_price_below_ma(df, index, ma_column='MA20'):
    """주가가 지정된 이동 평균 아래 있는지 확인"""
    close_price = df.loc[index, 'close']
    ma_price = df.loc[index, ma_column]
    return close_price < ma_price

def check_dead_cross(df, index):
    """Dead Cross 발생 여부 확인"""
    return df.loc[index, 'dead_cross']

def check_volume_below_ma(df, index, ma_column='MA5'):
    """거래량이 이동 평균보다 낮은지 확인"""
    volume = df.loc[index, 'volume']
    ma_volume = df.loc[index, ma_column]
    return volume < ma_volume

def check_stochrsi_decreasing(df, index, periods):
    """StochRSI가 감소하는지 확인"""
    if index < periods:
        return False  # 충분한 데이터가 없는 경우

    decreasing_k = True
    decreasing_d = True

    for i in range(index - periods + 1, index + 1):
        if i == 0: continue  # 첫 번째 인덱스는 건너뜀

        if df.loc[i, 'stochrsiK'] >= df.loc[i - 1, 'stochrsiK']:
            decreasing_k = False
        if df.loc[i, 'stochrsiD'] >= df.loc[i - 1, 'stochrsiD']:
            decreasing_d = False

    return decreasing_k and decreasing_d

def check_stochastic_dead_cross(df, index):
    # 주어진 인덱스에서 Stochastic RSI Dead Cross가 발생했는지 확인합니다.
    if index == 0:
        return False  # 첫 번째 인덱스에서는 비교할 이전 값이 없습니다.

    # 'stochrsiK'와 'stochrsiD'를 사용
    current_k = df.loc[index, 'stochrsiK']
    current_d = df.loc[index, 'stochrsiD']
    prev_k = df.loc[index-1, 'stochrsiK']
    prev_d = df.loc[index-1, 'stochrsiD']

    # Dead Cross 조건: 이전 K가 D 위였다가 현재 K가 D 아래로 교차
    return prev_k > prev_d and current_k < current_d


# 청산조건 함수 추가.

#  현재 posiiton 이 buy 인 경우.
def is_rsi_overbought(df, index, overbought_threshold=70):
    """RSI가 과매수 조건을 충족하는지 확인합니다."""
    rsi = df.loc[index, 'rsi']
    return rsi > overbought_threshold

def is_macd_crossdown(df, index):
    """MACD가 시그널 라인 아래로 내려가는지 확인합니다."""
    macd = df.loc[index, 'MACD']
    signal = df.loc[index, 'signal_macd']
    prev_macd = df.loc[index - 1, 'MACD']
    prev_signal = df.loc[index - 1, 'signal_macd']
    # MACD가 이전에는 시그널 위였으나 현재 시그널 아래로 내려갔는지 확인
    return prev_macd > prev_signal and macd < signal

# 현재 position 이 sell 인 경우.

def is_rsi_oversold(df, index, oversold_threshold=30):
    """RSI가 과매도 조건을 충족하는지 확인합니다."""
    rsi = df.loc[index, 'rsi']
    return rsi < oversold_threshold

def is_macd_crossup(df, index):
    """MACD가 시그널 라인 위로 올라가는지 확인합니다."""
    """MACD가 시그널 라인 위로 올라가는지 확인합니다."""
    macd = df.loc[index, 'MACD']
    signal = df.loc[index, 'signal_macd']
    prev_macd = df.loc[index - 1, 'MACD']
    prev_signal = df.loc[index - 1, 'signal_macd']
    # MACD가 이전에는 시그널 아래였으나 현재 시그널 위로 올라갔는지 확인
    return prev_macd < prev_signal and macd > signal

def is_price_stable(df, index, window=5, tolerance=0.005):
    """지정된 윈도우 내에서 가격이 안정적인지 확인합니다."""
    recent_prices = df['close'][index-window+1:index+1]
    sma = recent_prices.mean()
    price_stability = all(abs(price - sma) / sma <= tolerance for price in recent_prices)
    return price_stability