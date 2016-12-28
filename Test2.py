from __future__ import print_function, division
import numpy as np
import pandas as pd
import datetime as dt
#import pandas.io.data as web
import matplotlib.finance as mpf
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import tushare as ts
import datetime
from matplotlib import verbose, get_cachedir
from matplotlib.dates import date2num
from matplotlib.cbook import iterable, mkdirs
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import colorConverter
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D


if __name__ == '__main__':
    starttime = dt.date(2015,1,1)
    endtime = dt.date.today()
    ticker = 'SPY'
    fh = mpf.fetch_historical_yahoo(ticker, starttime, endtime)
    r = mlab.csv2rec(fh);
    fh.close()
    r.sort()
    df = pd.DataFrame.from_records(r)
    quotes = mpf.quotes_historical_yahoo_ohlc(ticker, starttime, endtime)
    fig, (ax1, ax2) = plt.subplots(2, sharex=True)
    tdf = df.set_index('date')
    cdf = tdf['close']
    cdf.plot(label = "close price", ax=ax1)
    pd.rolling_mean(cdf, window=30, min_periods=1).plot(label = "30-day moving averages", ax=ax1)
    pd.rolling_mean(cdf, window=10, min_periods=1).plot(label = "10-day moving averages", ax=ax1)
    ax1.set_xlabel(r'Date')
    ax1.set_ylabel(r'Price')
    ax1.grid(True)
    props = font_manager.FontProperties(size=10)
    leg = ax1.legend(loc='lower right', shadow=True, fancybox=True, prop=props)
    leg.get_frame().set_alpha(0.5)
    ax1.set_title('%s Daily' % ticker, fontsize=14)
    mpf.candlestick_ohlc(ax2, quotes, width=0.6)
    ax2.set_ylabel(r'Price')
    for ax in ax1, ax2:
        fmt = mdates.DateFormatter('%m/%d/%Y')
        ax.xaxis.set_major_formatter(fmt)
    ax.grid(True)
    ax.xaxis_date()
    ax.autoscale()
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.setp(plt.gca().get_xticklabels(), rotation=30)
    plt.show()
    fig.savefig('SPY.png')
