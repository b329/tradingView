# pythonProject
 
Trading Bot 의 기반이 되는 기본적인 파일을 공개합니다.
그리고 지난 시간의 백테스팅 결과를 함께 공유합니다.
백테스팅 결과는 확인해보면 대략 어떤 방식으로 로직이 움직이는지 알 수 있습니다.
다만, 세부적인 execute 로직은 private 에 남겨둡니다.

* TradingBot 의 백테스팅 결과의 한 예로 백테스팅결과_20240301_20240420_15days.zip 을 풀면 4개의 파일이 있습니다.
이 파일들을 Trading Bot 을 기간별로 백테스팅을 했을때 나오는 결과입니다.
1. 가장위에 BTCUSDT_graph_20240420_14.png 파일은 지난 데이터의 메수매도 포인트를 그림으로 표현 해준 데이터이고 어떤 지점에서 매수와 매도를 했는지를 눈으로 쉽게 볼 수 있게 표현해 주는 내용입니다.
2. combined_chart_data_BTCUSDT_20240420_14.csv 는 데이터 분석을 실시간으로 하면서 쌓인 데이 터라고 보면 됩니다.
3. filtered_chart_data_BTCUSDT_20240420_14.csv 는 combined_chart_data 가 양이 너무 많아서 보 기가 힘이 드니 실제 거래가 이루어진 지점을 filtering 해서 출력한 데이터로 데이터를 좀 더 편하게 확인하기 위 해 정제한 데이터입니다.
4. output_chart_data_BTCUSDT_origin_20240420_14.csv 는 Bot 이 실행되면서 저장하는 가징 기본이 되는 원시데이터 입니다.
위 파일 내용안에는 거래를 하기 위한 여러가지 보조지표들과 포인트 그리고 profit_rate 등이 기재되어 있는 것 을 확인할 수 있습니다.


I am releasing the basic files that form the foundation of the Trading Bot. I will also share the results of the backtesting from the last session. From the backtesting results, you can generally understand how the logic operates. However, the detailed execute logic will remain private.

1. As an example of the Trading Bot's backtesting results, when you extract the file named "backtesting_results_20240301_20240420_15days.zip," there are four files inside. These files represent the outcomes of period-specific backtesting for the Trading Bot.
2. The file named "BTCUSDT_graph_20240420_14.png" displays the buy and sell points of past data in a graphical format, making it easy to visually identify where buying and selling occurred.
3. The file "combined_chart_data_BTCUSDT_20240420_14.csv" can be seen as data accumulated in real-time during data analysis. "filtered_chart_data_BTCUSDT_20240420_14.csv" is a refined dataset created by filtering the data points where actual trades occurred from the much larger dataset in "combined_chart_data" to facilitate easier review.
4. Lastly, "output_chart_data_BTCUSDT_origin_20240420_14.csv" is the raw data that the Bot saves as it runs, which includes various auxiliary indicators, points, and the profit rate among other details.
   
