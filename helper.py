"""Helper functions for investment development app"""

import datetime
from dateutil.relativedelta import relativedelta

today = datetime.datetime.now()

def calculate_metric_gain_and_change(metric, df_development):
    """
    Calculate number for 1D, 1W, 1M, 6M, YTD, 1Y, 5Y, MAX metrics

    :param metric: One of 1D, 1W, 1M, 6M, YTD, 1Y, 5Y, MAX
    :type metric: str
    :param df_development: DataFrame with overall daily security development
    :type df_development: pandas.DataFrame

    :return: Gain or loss
    :rtype: str
    :return: Percentual change
    :rtype: str
    """

    # If the development to track is that of the whole investment period
    # or the investment started after Jan 1st, then we can just use the
    # last values of the DataFrame without doing further calculations
    max_date = df_development['Date'].max()

    # Calculate last date
    last_dates = {
        '1D': (max_date - relativedelta(days=1)).date(),
        '1W': (max_date - relativedelta(weeks=1)).date(),
        '1M': (max_date - relativedelta(months=1)).date(),
        '6M': (max_date - relativedelta(months=6)).date(),
        'YTD': datetime.date(day=1, month=1, year=today.year),
        '1Y': (max_date - relativedelta(years=1)).date(),
        '5Y': (max_date - relativedelta(years=5)).date(),
        'MAX': df_development['Date'].min().date()
    }

    df_after_date = df_development.loc[df_development['Date'].dt.date >= last_dates[metric]]
    if len(df_after_date) == 0:    # If no investments that long ago
        return '-', '-'

    first_close = df_after_date['Close'].iloc[0]
    last_close = df_development['Close'].iloc[-1]
    gain = last_close - first_close
    pct_change = 100 * (gain/first_close)

    gain = f'{'+' if gain >= 0 else ''}{gain:.2f}'
    pct_change = f'{pct_change:.2f}%'

    return gain, pct_change

def change_info_spelling(info):
    """
    Change spelling of descriptive information.

    :param info: Information to change spelling of.
    :type info: str

    :return: Changed spelling of info
    :rtype: str
    """

    replacements = {
        'EQUITY': 'Equity',
        'MUTUALFUND': 'Mutual Fund'
    }

    if info not in replacements:
        return info

    return replacements[info]
