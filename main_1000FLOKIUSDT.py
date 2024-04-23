import logging
import os
import time
from datetime import datetime, timedelta
import sys
import schedule

print(sys.path)

from binance.client import Client
from binance.exceptions import BinanceAPIException
from trading_logic import trade_logic


def job():
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    # 환경 변수 값이 제대로 설정되었는지 확인하기 위한 디버그 출력
    print("API Key:", api_key)  # 주의: 실제 운영 환경에서는 이 줄을 반드시 제거하거나 수정해야 합니다.
    print("API Secret:", api_secret)  # 주의: 실제 운영 환경에서는 이 줄을 반드시 제거하거나 수정해야 합니다.

    client = Client(api_key, api_secret)
    chain = '1000FLOKIUSDT'
    interval_15m = '15m'
    interval_1h = '1h'
    interval_4h = '4h'
    divisions = 20  # 여기에서 divisions 값을 설정합니다.

    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

    # 손절매 기준 손실률 설정
    loss_threshold = -0.005  # 예: 0.5% 손실률
    # long -1.0 이라는 의미는 long 에서는 청산하지 않음.
    when_long_loss_threshold = -0.005
    when_short_loss_threshold = -0.005
    bollinger_multiplier = 2.0
    increase_threshold = 1.03
    decrease_threshold = 0.97
    bollinger_band_width = 500
    use_close_bands_for_buy = True,
    use_close_bands_for_sell = True

    def get_timeframe(use_fixed_endtime=False):
        if use_fixed_endtime:
            # endtime을 설정 (예: 2024년 2월 28일 01:30 UTC)
            endtime_str = "2024-04-1 13:00"
            endtime_format = "%Y-%m-%d %H:%M"
            endtime = datetime.strptime(endtime_str, endtime_format)

            # 15일 이전의 시간을 계산
            starttime = endtime - timedelta(days=15)

            # starttime을 문자열로 변환
            starttime_str = starttime.strftime(endtime_format)

            return starttime_str, endtime_str
        else:
            # 상대적인 시간 사용 (예: '15 day ago UTC')
            starttime_str = '15 day ago UTC'
            # 'endtime'은 사용하지 않음
            return starttime_str, None

    # 고정된 'endtime' 사용하려면:
    # 또는 'endtime' 없이 상대적인 'starttime'만 사용하려면:
    # starttime, endtime = get_timeframe(use_fixed_endtime=True)
    starttime, endtime = get_timeframe(use_fixed_endtime=False)


    # 설정 변수들
    settings = {
        'leverage': 4,  # 초기 레버리지 값 설정
        'bollinger_settings': {
            'multiplier': bollinger_multiplier,
            'increase_threshold': increase_threshold,
            'decrease_threshold': decrease_threshold,
            'band_width_threshold': bollinger_band_width,
            'use_close_bands_for_buy': use_close_bands_for_buy,
            'use_close_bands_for_sell': use_close_bands_for_sell,
            'stochrsi_periods': 3,
            'golden_cross_periods': 3,  # Check if golden cross occurred in the last 5 periods
            'dead_cross_periods': 3
        },
        'stoch_rsi_settings': {
            'stochrsi_periods': 14,
            'smoothK': 3,
            'smoothD': 3
        },
        'liquidation_settings': {
            'loss_threshold': loss_threshold,  # 예: 0.02 : 2% 손실률
            'when_long_loss_threshold': when_long_loss_threshold,  # long 일 경우
            'when_short_loss_threshold': when_short_loss_threshold,  # short 일 경우
            'profit_target': 5,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'profit_thresholds': {
                'buy': {'positive': 0.0036, 'negative': -0.0071},  # long 포지션을 위한 수익률 범위
                'sell': {'positive': 0.0036, 'negative': -0.0071}  # short 포지션을 위한 수익률 범위
            }
        },

        # 메인 설정에 price_stability_settings 추가
        # is_price_stable 함수가 가격이 안정적이지 않을 때 거래를 실행하길 원한다면, tolerance 값을 작게 설정하는 것이 좋다.
        # 이렇게 설정하면, 작은 가격 변동도 시장의 불안정성으로 간주되어, 가격 안정성 조건이 False로 평가될 가능성이 높아진다.
        # 이 경우, 가격 변동성이 높을 때 포지션을 개시하거나 청산하는 전략에 부합한다.

        'price_stability_settings': {
            'make_position': {'window': 5, 'tolerance': 0.009},  # 신규 포지션 개시 시 사용
            'liquidation': {'window': 5, 'tolerance': 0.55}  # 청산 시 사용
        },
        'multi_timeframe_settings': {
            'use_1h_trend': True,
            'use_4h_trend': True
        },
        'initial_capital': 40000000,  # 초기 자본금 설정, 예: 2000000 만원
    }

    # 가능한 options
    # interval = '1m'
    # interval = '15m'
    # interval = '1h'
    # interval = '4h'

    trade_logic(client, chain, interval_15m, interval_1h, interval_4h, settings, starttime, endtime, divisions)
    print("Trade logic executed successfully.")


def main():
    # 5분마다 job 함수를 실행
    # schedule.every(15).minutes.do(job)
    schedule.every(5).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
