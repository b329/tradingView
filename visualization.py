import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from PIL import Image
import datetime
import os


def plot_bollinger_bands_macd_rsi_adx_graph(chain, symbol_df, df_1h, backdata_directory):
    # 날짜를 datetime 객체로 변환합니다.
    symbol_df['date'] = pd.to_datetime(symbol_df['date'])
    # 시각화를 위해 날짜 형식을 datetime으로 변환합니다.
    df_1h['date'] = pd.to_datetime(df_1h['date'])

    # 데이터를 15일 간격으로 분리
    start_date = symbol_df['date'].min()
    end_date = symbol_df['date'].max()
    period = datetime.timedelta(days=15)

    while start_date <= end_date:
        current_end_date = min(start_date + period, end_date)
        # 현재 기간에 해당하는 데이터 필터링
        current_symbol_df = symbol_df[(symbol_df['date'] >= start_date) & (symbol_df['date'] <= current_end_date)]
        current_df_1h = df_1h[(df_1h['date'] >= start_date) & (df_1h['date'] <= current_end_date)]

        # df_1h 기준 골든 크로스와 데드 크로스에 대한 마커를 ax1에 추가
        stochrsi_golden_cross_points = current_df_1h[current_df_1h['stochrsi_golden_cross'] == True]
        stochrsi_dead_points = current_df_1h[current_df_1h['stochrsi_dead_cross'] == True]

        # 파일 이름에 시작 날짜와 끝나는 날짜를 포함
        file_start_date = start_date.strftime("%Y%m%d")
        file_end_date = current_end_date.strftime("%Y%m%d")
        png_filename = os.path.join(backdata_directory, f"{chain}_graph_{file_start_date}_to_{file_end_date}.png")

        # 메인 차트 (주가 및 볼린저 밴드)
        # plt.style.use('dark_background')  # 전체 배경을 검은색으로 설정
        fig, (ax1, ax2) = plt.subplots(2, figsize=(20, 12), dpi=150, gridspec_kw={'height_ratios': [4, 2]})

        # 1시간 차트의 MA20 추가
        ax1.plot(current_df_1h['date'], current_df_1h['MA10'], label='1H MA10', color='purple', linewidth=1)
        ax1.plot(current_df_1h['date'], current_df_1h['MA5'], label='1H MA5', color='orange', linewidth=1,
                 linestyle='--')  # 5MA 추가

        ax1.scatter(stochrsi_golden_cross_points['date'], stochrsi_golden_cross_points['MA5'], color='gold', marker='*',
                    s=50,
                    label='1H StochRSI Golden Cross')
        ax1.scatter(stochrsi_dead_points['date'], stochrsi_dead_points['MA5'], color='black', marker='X', s=50,
                    label='1H StochRSI Dead Cross', linewidths=0.2)  # 더 얇은 'x', 색상 및 크기 조정
        # 15분 차트 데이터 표시
        ax1.plot(current_symbol_df['date'], current_symbol_df['close'], label='Close', linewidth=0.5)
        ax1.plot(current_symbol_df['date'], current_symbol_df['MA10'], label='15M MA10', linewidth=0.5)
        ax1.plot(current_symbol_df['date'], current_symbol_df['MA5'], label='15M MA5', color='blue', linewidth=0.5)
        ax1.plot(current_symbol_df['date'], current_symbol_df['upper'], label='Upper Band', linewidth=0.5)
        ax1.plot(current_symbol_df['date'], current_symbol_df['lower'], label='Lower Band', linewidth=0.5)
        ax1.fill_between(current_symbol_df['date'], current_symbol_df['lower'], current_symbol_df['upper'],
                         color='grey', alpha=0.3)

        # 1시간 차트 볼린저 밴드 추가
        ax1.plot(current_df_1h['date'], current_df_1h['MA10'], label='1H MA10', color='purple', linewidth=1,
                 linestyle='--')
        ax1.plot(current_df_1h['date'], current_df_1h['upper'], label='1H Upper Band', color='red', linewidth=0.75,
                 linestyle='--')
        ax1.plot(current_df_1h['date'], current_df_1h['lower'], label='1H Lower Band', color='green', linewidth=0.75,
                 linestyle='--')

        # 주석 추가 함수
        def add_annotations(ax, df, event_column, marker, color, label):
            event_points = df[df[event_column] == True]
            for _, point in event_points.iterrows():
                ax.scatter(point['date'], point['close'], color=color, label=label, marker=marker, alpha=1, s=100)
                ax.annotate(point['date'].strftime('%Y-%m-%d %H:%M'), (point['date'], point['close']),
                            textcoords="offset points", xytext=(0, 10), ha='center')

        # 매수, 매도, 청산, 손절매 포인트에 대한 주석 추가
        # 이 부분은 기존의 코드를 사용하여 15분 차트의 이벤트를 표시합니다.
        # 여기에 1시간 차트의 골든 크로스 및 데드 크로스 이벤트를 추가하려면,
        # df_1h 데이터에서 해당 이벤트를 식별할 수 있는 컬럼이 필요합니다.
        # 예시: add_annotations(ax1, df_1h, 'golden_cross', '*', 'gold', '1H Golden Cross')

        # 매수, 매도, 청산, 손절매 포인트에 대한 주석 추가
        add_annotations(ax1, current_symbol_df, 'buy', '^', 'green', 'Buy')
        add_annotations(ax1, current_symbol_df, 'sell', 'v', 'red', 'Sell')
        add_annotations(ax1, current_symbol_df, 'liquidation_from_buy', 'v', 'blue', 'Liquidation from Buy')
        add_annotations(ax1, current_symbol_df, 'liquidation_from_sell', '^', 'magenta', 'Liquidation from Sell')
        add_annotations(ax1, current_symbol_df, 'loss_cut_from_buy', 'x', 'black', 'Loss Cut from Buy')
        add_annotations(ax1, current_symbol_df, 'loss_cut_from_sell', 'x', 'black', 'Loss Cut from Sell')

        # 중복된 범례 항목 제거
        handles, labels = ax1.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))  # 중복 제거
        ax1.set_ylabel('Close price', fontsize=18)
        ax1.legend(by_label.values(), by_label.keys(), loc='upper left')

        # x축에 날짜 포맷 설정
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        # 두 번째 차트: 스토캐스틱 RSI
        ax2.plot(current_symbol_df['date'], current_symbol_df['stochrsiK'], label='StochRSI K', color='blue')
        ax2.plot(current_symbol_df['date'], current_symbol_df['stochrsiD'], label='StochRSI D', color='orange')
        ax2.fill_between(current_symbol_df['date'], y1=20, y2=80, color='gray', alpha=0.3)

        # 여기서는 stochrsi_golden_cross 및 stochrsi_dead_cross에 대한 주석 추가가 필요 없을 수 있습니다.
        # 필요하다면 위의 add_annotations 방식을 사용하여 추가할 수 있습니다.

        ax2.set_ylabel('StochRSI', fontsize=18)
        ax2.set_xlabel('Date', fontsize=18)
        ax2.legend(loc='upper left')

        # 파일 저장 및 닫기
        plt.savefig(png_filename, dpi=300)
        plt.close()

        # 다음 기간 설정
        start_date += period
