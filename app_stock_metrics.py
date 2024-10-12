"""A simple security development dashboard"""

import plotly.express as px
import streamlit as st
import yfinance as yf
import helper

st.set_page_config(
    page_title='Security Development Dashboard',
    page_icon=':chart_with_upwards_trend:',
    layout='wide'
)

st.title('Security Development Dashboard')
st.write(
    '''
    This app allows you to analyse the development of 
    securities (tradable financial assets) over time.
    '''
)

# Ask user to input ticker symbol or ISIN code
input_cols = st.columns(2)

tickers_input = input_cols[0].text_input(
    label='What securities would you like to analyse?',
    placeholder='Enter ticker symbols or ISIN codes separated by commas (AAPL,MSFT,US88160R1014)',
    help='''
    A ticker symbol or stock symbol is an abbreviation used to uniquely identify publicly 
    traded shares of a particular stock or security on a particular stock exchange.

    An International Securities Identification Number (ISIN) is a code that uniquely identifies 
    a security globally for the purposes of facilitating clearing, reporting and settlement of trades.
    '''
)

# Format text input
tickers_input = tickers_input.replace(' ', '')  # Remove whitespaces
if tickers_input == '':
    st.write('Please enter at least one ticker symbol.')
else:
    tickers_input = tickers_input.split(',')          # Get list from text input
    tickers_input = set(tickers_input)                # Remove duplicates
    tickers = {}                                      # Dict of symbol - yf.Ticker
    ticker_names = {}                                 # Dict of symbol - security name

    # Get ticker objects and store them in dictionary
    for ti in tickers_input:
        ticker = yf.Ticker(ti)
        security_exists = ticker.info != {'trailingPegRatio': None}
        if not security_exists:
            st.write(f'No data was found for {ti}.')
        else:
            symbol = ticker.info['symbol']
            tickers[symbol] = ticker
            if 'longName' in ticker.info:
                ticker_names[symbol] = f'{ticker.info['longName']} ({symbol})'
            elif 'shortName' in ticker.info:
                ticker_names[symbol] = f'{ticker.info['shortName']} ({symbol})'
            else:
                ticker_names[symbol] = symbol

    # Display each security performance in its own tab
    ticker_names = dict(sorted(ticker_names.items(), key=lambda item: item[1]))
    tabs = st.tabs(ticker_names.values())

    for tab_idx, symbol in enumerate(ticker_names.keys()):
        with tabs[tab_idx]:
            # Download security data
            if f'data_{symbol}' not in st.session_state:
                df_development = yf.download(
                    tickers=symbol
                )

                if len(df_development) == 0:
                    st.write(f'No data was found for {symbol}.')
                    continue

                # Date as column instead of index
                df_development = df_development.reset_index()
                st.session_state[f'data_{symbol}'] = df_development

            df_development = st.session_state[f'data_{symbol}'].copy()

            # Calculate the price change over a period of time
            # and display metrics horizontally
            metrics = ['1D', '1W', '1M', '6M', 'YTD', '1Y', '5Y', 'MAX']
            cols_metrics = st.columns(len(metrics))
            for col_idx, metric in enumerate(metrics):
                gain, change_pct = helper.calculate_metric_gain_and_change(
                    metric,
                    df_development
                )

                cols_metrics[col_idx].metric(
                    label=metric,
                    value=gain,
                    delta=change_pct,
                    delta_color='off' if change_pct == '-' else 'normal'
                )

            # Plot development
            fig_development = px.line(
                df_development.reset_index(),
                x='Date',
                y='Close',
                title=ticker_names[symbol]
            )

            Y_AXIS_TITLE = 'Close Price'
            is_currency_known = 'currency' in tickers[symbol].info
            if is_currency_known:
                Y_AXIS_TITLE += f' ({tickers[symbol].info['currency']})'

            fig_development.update_layout(
                xaxis_title='Date',
                yaxis_title=Y_AXIS_TITLE
            )

            st.plotly_chart(fig_development, use_container_width=True)

            # Display additional information
            key_and_info = {
                'quoteType': 'Security Type',
                'industry': 'Industry',
                'sector': 'Sector',
                'financialCurrency': 'Financial Currency'
            }

            # Display only those keys that appear in ticker info
            info_existing = {k:i for k,i in key_and_info.items() if k in tickers[symbol].info}
            cols_info = st.columns(len(info_existing))
            for i, (key, info_type) in enumerate(info_existing.items()):
                cols_info[i].subheader(info_type)
                info = tickers[symbol].info[key]
                info = helper.change_info_spelling(info)
                cols_info[i].write(info)

            st.divider()

            if 'longBusinessSummary' in tickers[symbol].info:
                st.subheader('Summary')
                # https://discuss.streamlit.io/t/using-st-write-with-sign-gives-formatted-text/48387
                st.write(tickers[symbol].info['longBusinessSummary'].replace('$', r'\$'))
