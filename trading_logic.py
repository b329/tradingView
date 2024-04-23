from data_processing import get_data_frame
import pandas as pd
import numpy as np
import talib as ta
from indicators import Stoch, calculate_stoch_rsi, calculate_stoch_rsi_crosses, calculate_moving_average_crosses
from indicators import (is_increasing_consecutively, is_decreasing_consecutively,
                        is_stochrsi_increasing, has_golden_cross_occurred,
                        is_stochrsi_decreasing, has_dead_cross_occurred,
                        calculate_moving_averages, calculate_bollinger_bands,
                        calculate_macd, calculate_band_conditions, calculate_volume_change_pct)
from utils import extract_settings
from visualization import plot_bollinger_bands_macd_rsi_adx_graph
from conditions import (check_bollinger_band_width, check_price_above_ma, check_golden_cross, check_volume_above_ma,
                        check_stochrsi_increasing, check_stochastic_golden_cross, check_stochastic_dead_cross,
                        is_rsi_overbought, is_macd_crossdown, is_rsi_oversold, is_macd_crossup, is_price_stable,
                        check_price_below_ma, check_dead_cross, check_volume_below_ma, check_stochrsi_decreasing)

from binance_api_utils import (execute_divided_orders_with_latest_price,
                               execute_divided_liquidation, execute_loss_cut_orders, get_leveraged_balance,
                               informatio_de_positio_reali)

import datetime
import time
import logging
import os

# 환경 변수에서 테스트 모드 여부를 확인
modus_probatio_est = os.getenv('MODUS_PROBATIO_EST') == 'True'
print(f"Modus Probatio Est: {modus_probatio_est}")

# Assuming 'backdata' is a directory in the same location as your script
backdata_directory = "backdata"
# Ensure the directory exists
os.makedirs(backdata_directory, exist_ok=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def trade_logic(client, chain, interval_15m, interval_1h, interval_4h, settings, starttime, endtime, divisions):
    # 레버리지 값 출력
    global modus_probatio_est
    print(f"Setting leverage for {chain} to {settings['leverage']}")

    symbol_df = get_data_frame(client, chain, interval_15m, starttime, endtime)
    # df_15m = get_data_frame(client, chain, interval_15m, starttime, endtime)
    df_1h = get_data_frame(client, chain, interval_1h, starttime, endtime)
    df_4h = get_data_frame(client, chain, interval_4h, starttime, endtime)

    # extract_settings 함수를 사용하여 모든 설정 값들을 추출합니다.
    extracted_settings = extract_settings(settings)
    # 추출된 설정 값들을 사용합니다.
    bollinger_settings = extracted_settings['bollinger_settings']
    stoch_rsi_settings = extracted_settings['stoch_rsi_settings']
    liquidation_settings = extracted_settings['liquidation_settings']
    price_stability_settings = extracted_settings['price_stability_settings']
    multi_timeframe_settings = extracted_settings['multi_timeframe_settings']

    # 초기 자본금 설정
    current_capital = extracted_settings['initial_capital']

    # 지표 계산
    symbol_df = calculate_moving_averages(symbol_df, [5, 10])
    symbol_df = calculate_bollinger_bands(symbol_df, period=20, bollinger_multiplier=bollinger_settings['multiplier'],
                                          increase_threshold=bollinger_settings['increase_threshold'],
                                          decrease_threshold=bollinger_settings['decrease_threshold'])
    symbol_df = calculate_macd(symbol_df)
    # 데이터프레임에 지표 추가
    symbol_df = calculate_band_conditions(symbol_df)

    # Stochastic RSI 및 그것의 골든 크로스와 데드 크로스 계산
    symbol_df = calculate_stoch_rsi(symbol_df, period=stoch_rsi_settings['stochrsi_periods'],
                                    smoothk=stoch_rsi_settings['smoothK'], smoothd=stoch_rsi_settings['smoothD'])
    symbol_df = calculate_stoch_rsi_crosses(symbol_df)

    # short_period=5 : 5MA, long_period=10 : 10MA
    symbol_df = calculate_moving_average_crosses(symbol_df, short_period=5, long_period=10)

    symbol_df = calculate_volume_change_pct(symbol_df)

    # 1시간 차트 데이터에 적용
    df_1h = calculate_bollinger_bands(df_1h, period=20, bollinger_multiplier=bollinger_settings['multiplier'],
                                      increase_threshold=bollinger_settings['increase_threshold'],
                                      decrease_threshold=bollinger_settings['decrease_threshold'])
    df_1h = calculate_stoch_rsi(df_1h, period=14, smoothk=3, smoothd=3)
    df_1h = calculate_stoch_rsi_crosses(df_1h)
    df_1h = calculate_moving_averages(df_1h, [5, 10])  # 5, 10일 이동 평균선 추가
    df_1h = calculate_volume_change_pct(df_1h)

    df_1h = calculate_macd(df_1h)
    df_1h = calculate_band_conditions(df_1h)

    # 이동 평균의 추세 확인을 위해 이전 값을 계산 (예: 1일 전의 20일 이동 평균)
    df_1h['MA10_prev'] = df_1h['MA10'].shift(1)
    # 추세 확인: MA10이 MA10_prev보다 크면 상승 추세, 작으면 하락 추세
    df_1h['MA10_trend'] = df_1h.apply(
        lambda row: 'up' if row['MA10'] > row['MA10_prev'] else ('down' if row['MA10'] < row['MA10_prev'] else 'flat'),
        axis=1)

    # 4시간 차트 데이터에 적용
    df_4h = calculate_bollinger_bands(df_4h, period=20, bollinger_multiplier=bollinger_settings['multiplier'],
                                      increase_threshold=bollinger_settings['increase_threshold'],
                                      decrease_threshold=bollinger_settings['decrease_threshold'])
    df_4h = calculate_stoch_rsi(df_4h, period=14, smoothk=3, smoothd=3)
    df_4h = calculate_stoch_rsi_crosses(df_4h)
    df_4h = calculate_moving_averages(df_4h, [5, 10])  # 5, 10일 이동 평균선 추가
    df_4h = calculate_volume_change_pct(df_4h)

    df_4h = calculate_macd(df_4h)
    df_4h = calculate_band_conditions(df_4h)

    df_4h['MA10_prev'] = df_4h['MA10'].shift(1)
    df_4h['MA10_trend'] = df_4h.apply(
        lambda row: 'up' if row['MA10'] > row['MA10_prev'] else ('down' if row['MA10'] < row['MA10_prev'] else 'flat'),
        axis=1)

    # 극적으로 변할 수 있는 것을 받아들임 또는 극변을 수용.
    drastically_changeable_accept = True  # 또는 False

    # check buy logic
    # 핵심로직 trading logic 구현 (공개 github 에서는 삭제되었음.)
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현
    # 핵심로직 trading logic 구현 (공개 github 에서는 삭제되었음.)

    print(f"df_combined['close']: {df_combined['close'].iloc[-1]}")
    print(f"df_combined['MA20']: {df_combined['MA20'].iloc[-1]}")
    print(f"df_combined['close']가 'MA20'보다 작은가? : {df_combined['close'].iloc[-1] < df_combined['MA20'].iloc[-1]}")
    print(f"df_combined['close']가 'MA20'보다 큰가? : {df_combined['close'].iloc[-1] > df_combined['MA20'].iloc[-1]}")

    current_time = datetime.datetime.now().strftime("%Y%m%d_%H")
    # 기존 데이터프레임을 "_origin" 파일로 저장
    original_filename = os.path.join(backdata_directory, f'output_chart_data_{chain}_origin_{current_time}.csv')
    symbol_df.to_csv(original_filename, index=True)

    # 통합 데이터를 CSV 파일로 저장합니다.
    combined_csv_filename = os.path.join(backdata_directory, f'combined_chart_data_{chain}_{current_time}.csv')
    df_combined.to_csv(combined_csv_filename, index=False)

    # buy 또는 sell 컬럼에 True가 있는 행만 필터링
    # buy, sell 또는 liquidation 관련 컬럼에 값이 있는 행만 필터링
    # 필요한 컬럼들을 미리 확인하고 초기화
    columns_to_check = [
        'sell_price', 'buy_price', 'profit_rate_from_liquidation_sell',
        'profit_rate_from_liquidation_buy', 'profit_rate_from_loss_cut_sell',
        'profit_rate_from_loss_cut_buy', 'liquidation_from_sell_price',
        'liquidation_from_buy_price'
    ]

    for col in columns_to_check:
        if col not in df_combined.columns:
            df_combined[col] = np.nan  # 컬럼이 없으면 NaN 값으로 초기화

    filtered_df = df_combined[
        (df_combined['sell_price'].notna()) |
        (df_combined['buy_price'].notna()) |
        (df_combined['profit_rate_from_liquidation_sell'].notna()) |
        (df_combined['profit_rate_from_liquidation_buy'].notna()) |
        (df_combined['profit_rate_from_loss_cut_sell'].notna()) |
        (df_combined['profit_rate_from_loss_cut_buy'].notna()) |
        (df_combined['liquidation_from_sell_price'].notna()) |
        (df_combined['liquidation_from_buy_price'].notna())]

    # 청산된 매수 및 매도 포지션의 수익률 합계를 요약 행에 추가
    # 요약 행을 DataFrame으로 생성
    summary_df = pd.DataFrame([{
        'sum_profit_rate_from_liquidation_buy_position': sum_profit_rate_buy,
        'sum_profit_rate_from_liquidation_sell_position': sum_profit_rate_sell
    }])

    # filtered_df에 요약 행을 추가
    filtered_df = pd.concat([filtered_df, summary_df], ignore_index=True)

    # 필터링된 데이터프레임을 "_filtered" 파일로 저장
    filtered_filename = os.path.join(backdata_directory, f'filtered_chart_data_{chain}_{current_time}.csv')
    filtered_df.to_csv(filtered_filename, index=True)

    # 이 함수는 주가 데이터프레임에서 Bollinger Bands와 함께 주가 차트를 그리고,
    # 매수와 매도 지점을 나타내는 마커를 추가합니다. x, y 축 레이블과 범례도 함께 추가되어 있습니다.
    modus_probatio_est = os.getenv('MODUS_PROBATIO_EST', 'False') == 'True'
    if modus_probatio_est:
        # 테스트 모드인 경우에만 그래프 함수 실행. 그림을 운영에 저장할 이유가 없음.
        plot_bollinger_bands_macd_rsi_adx_graph(chain, df_combined, df_1h, backdata_directory)

    # 여기 윗 라인 까지는 graph 를 그려서 히스토리로 값을 유추하기 위한 과정.

    # sudo code 추가
    # 1. 현재 계좌를 실시간으로 조회하여 Futures position 에서 long 포지션이 있는 경우에는 print('BUY') 로직을 실행하지 않고 건너 뛰도록 한다.
    # 2. 현재 계좌를 실시간으로 조회하여 Futures position 에서 아래 조건이 만족하는 경우 현재 보유자산을 레버리지 2배수로 80% long position 을 실행한다.
    # 3. 2변이 체결이 정상적으로 되었다는 신호를 받으면 바로 loss cut 을 주문을 하는데 손익비가 -3% 가 되는 시점에 시장가로 해당 포지션을 종료하는 주문을 미리 넣어둔다.

    # leverage config, 이건 앞으로도 수동으로 바꾸는 것으로
    # client.futures_change_leverage(symbol=chain, leverage=4)
