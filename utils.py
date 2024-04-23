def extract_settings(settings):
    # Bollinger Bands 설정 추출
    bollinger_settings = settings.get('bollinger_settings', {})
    bollinger_multiplier = bollinger_settings.get('multiplier', 2.0)
    increase_threshold = bollinger_settings.get('increase_threshold', 1.07)
    decrease_threshold = bollinger_settings.get('decrease_threshold', 0.93)
    band_width_threshold = bollinger_settings.get('band_width_threshold', 700)
    use_close_bands_for_buy = bollinger_settings.get('use_close_bands_for_buy', True)
    use_close_bands_for_sell = bollinger_settings.get('use_close_bands_for_sell', True)
    stochrsi_periods = bollinger_settings.get('stochrsi_periods', 14)
    golden_cross_periods = bollinger_settings.get('golden_cross_periods', 5)
    dead_cross_periods = bollinger_settings.get('dead_cross_periods', 5)

    stoch_rsi_settings = settings.get('stoch_rsi_settings', {})  # 이 줄이 중요
    stochrsi_periods = stoch_rsi_settings.get('stochrsi_periods', 14)
    smoothK = stoch_rsi_settings.get('smoothK', 3)
    smoothD = stoch_rsi_settings.get('smoothD', 3)

    # Liquidation 설정 추출
    liquidation_settings = settings.get('liquidation_settings', {})
    loss_threshold = liquidation_settings.get('loss_threshold', -0.015)
    when_long_loss_threshold = liquidation_settings.get('when_long_loss_threshold', -0.31)
    when_short_loss_threshold = liquidation_settings.get('when_short_loss_threshold', -0.011)
    profit_target = liquidation_settings.get('profit_target', 5)
    rsi_overbought = liquidation_settings.get('rsi_overbought', 70)
    rsi_oversold = liquidation_settings.get('rsi_oversold', 30)

    # Price Stability 설정 추출
    price_stability_settings = settings.get('price_stability_settings', {})
    make_position_stability_window = price_stability_settings.get('make_position', {}).get('window', 5)
    make_position_stability_tolerance = price_stability_settings.get('make_position', {}).get('tolerance', 0.005)
    liquidation_stability_window = price_stability_settings.get('liquidation', {}).get('window', 5)
    liquidation_stability_tolerance = price_stability_settings.get('liquidation', {}).get('tolerance', 0.005)

    # Multi Timeframe 설정 추출
    multi_timeframe_settings = settings.get('multi_timeframe_settings', {})
    use_1h_trend = multi_timeframe_settings.get('use_1h_trend', False)
    use_4h_trend = multi_timeframe_settings.get('use_4h_trend', False)

    # initial_capital 설정 추출
    initial_capital = settings.get('initial_capital', 2000000)

    return {
        'bollinger_settings': {
            'multiplier': bollinger_multiplier,
            'increase_threshold': increase_threshold,
            'decrease_threshold': decrease_threshold,
            'band_width_threshold': band_width_threshold,
            'use_close_bands_for_buy': use_close_bands_for_buy,
            'use_close_bands_for_sell': use_close_bands_for_sell,
            'stochrsi_periods': stochrsi_periods,
            'golden_cross_periods': golden_cross_periods,
            'dead_cross_periods': dead_cross_periods
        },
        'stoch_rsi_settings': {
            'stochrsi_periods': stochrsi_periods,
            'smoothK': smoothK,
            'smoothD': smoothD
        },
        'liquidation_settings': {
            'loss_threshold': loss_threshold,
            'when_long_loss_threshold': when_long_loss_threshold,
            'when_short_loss_threshold': when_short_loss_threshold,
            'profit_target': profit_target,
            'rsi_overbought': rsi_overbought,
            'rsi_oversold': rsi_oversold
        },
        'price_stability_settings': {
            'make_position': {
                'window': make_position_stability_window,
                'tolerance': make_position_stability_tolerance
            },
            'liquidation': {
                'window': liquidation_stability_window,
                'tolerance': liquidation_stability_tolerance
            }
        },
        'multi_timeframe_settings': {
            'use_1h_trend': use_1h_trend,
            'use_4h_trend': use_4h_trend
        },
        'initial_capital': initial_capital
    }
