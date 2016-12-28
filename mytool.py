# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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
from matplotlib import pyplot as plt
from matplotlib.dates import *
import matplotlib as matplotlib
import os
from mpl_toolkits.axes_grid1.axes_rgb import make_rgb_axes, RGBAxes
import numpy
from matplotlib.ticker import FixedLocator, MultipleLocator, FuncFormatter, NullFormatter
import math
import matplotlib.font_manager as font_manager

__color_lightsalmon__ = '#ffa07a'
__color_pink__ = '#ffc0cb'
__color_navy__ = '#000080'

def m_candlestick(ax1, ax2, df, width=1, colorup='r', colordown='g',
                 alpha=1.0):

    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    df : pandas data from tushare
    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level
    ochl: bool
        argument to select between ochl and ohlc ordering of quotes

    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added

    """

    OFFSET = width / 2

    lines = []
    patches = []

    m_date_time = []
    ma5_line  = []
    ma10_line = []
    ma20_line = []

    for date_string,row in df.iterrows():
        date_time = datetime.datetime.strptime(date_string,'%Y-%m-%d')
        t = date2num(date_time)

        open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20 = row[:10]
            # = row[7:9]
        if volume > 0:
            if close >= open:
                color = colorup
                lower = open
                height = close - open
            else:
                color = colordown
                lower = close
                height = open - close

            vline = Line2D(
                xdata=(t, t), ydata=(low, high),
                color=color,
                linewidth=0.8,
                antialiased=True,
            )

            rect = Rectangle(
                xy=(t - OFFSET, lower),
                width=width,
                height=height,
                facecolor=color,
                edgecolor=color,
            )
            rect_volum = Rectangle(
                xy=(t - OFFSET, 0),
                width=width,
                height=volume,
                facecolor=color,
                edgecolor=color,
            )
            rect.set_alpha(alpha)
            lines.append(vline)
            patches.append(rect)
            ax1.add_line(vline)
            ax1.add_patch(rect)
            ax2.add_patch(rect_volum)

            #收集 时间 MA 数据
            m_date_time.append(t)
            ma5_line.append(ma5)
            ma10_line.append(ma10)
            ma20_line.append(ma20)

    #画MA 均线
    ax1.plot(m_date_time, ma5_line, color='b')
    ax1.plot(m_date_time, ma10_line, color='y')
    ax1.plot(m_date_time, ma20_line, color='c')

    ax1.autoscale_view()

    return lines, patches

def drawPic(df, code, name):
    mondays = WeekdayLocator(MO)                # 主要刻度
    alldays = DayLocator()                      # 次要刻度
    #weekFormatter = DateFormatter('%b %d')     # 如：Jan 12
    mondayFormatter = DateFormatter('%m-%d-%Y') # 如：2-29-2015
    dayFormatter = DateFormatter('%d')          # 如：12
    zhfont = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simsun.ttc')
    __font_properties__ = font_manager.FontProperties(fname='C:\Windows\Fonts\simsun.ttc')

    highest_price = df['close'].max()
    lowest_price = df['close'].min()
    # === 初始化 Figure 需要的变量 =======================================================================
    length_x = len(df)
    xfactor = 10.0 / 230.0  # 一条 K 线的宽度在 X 轴上所占距离（英寸）
    yfactor = 0.3  # Y 轴上每一个距离单位的长度（英寸），这个单位距离是线性坐标和对数坐标通用的

    yhighlim_price = int(highest_price * 1.1)  # K线子图 Y 轴最大坐标
    ylowlim_price = int(lowest_price / 1.1)  # K线子图 Y 轴最小坐标

    expbase = 1.1  # 底数，取得小一点，比较接近 1。股价 3 元到 4 元之间有大约 3 个单位距离
    ymulti_price = math.log(yhighlim_price, expbase) - math.log(ylowlim_price, expbase)

    ymulti_vol = 3.0  # 成交量部分在 Y 轴所占的 “份数”
    ymulti_top = 1.2  # 顶部空白区域在 Y 轴所占的 “份数”
    ymulti_bot = 1.2  # 底部空白区域在 Y 轴所占的 “份数”

    xmulti_left = 12.0  # 左侧空白区域所占的 “份数”
    xmulti_right = 12.0  # 右侧空白区域所占的 “份数”

    xmulti_all = length_x + xmulti_left + xmulti_right
    xlen_fig = xmulti_all * xfactor  # 整个 Figure 的宽度
    ymulti_all = ymulti_price + ymulti_vol + ymulti_top + ymulti_bot
    ylen_fig = ymulti_all * yfactor  # 整个 Figure 的高度

    rect_1 = (xmulti_left / xmulti_all, (ymulti_bot + ymulti_vol) / ymulti_all, length_x / xmulti_all,
              ymulti_price / ymulti_all)  # K线图部分
    rect_2 = (
    xmulti_left / xmulti_all, ymulti_bot / ymulti_all, length_x / xmulti_all, ymulti_vol / ymulti_all)  # 成交量部分

    # === 建立 Figure 对象 =======================================================================
    figfacecolor = __color_pink__
    figedgecolor = __color_navy__
    figdpi = 300
    figlinewidth = 1.0

    #figobj = plt.figure(figsize=(xlen_fig, ylen_fig), dpi=figdpi, facecolor=figfacecolor, edgecolor=figedgecolor,
    #                       linewidth=figlinewidth)  # Figure 对象
    fig, (ax1, ax2) = plt.subplots(2, sharex=True)
    # ==================================================================================================================================================
     # =======    XXX:  成交量
    # ==================================================================================================================================================

    # === 添加\设置 Axis 对象 格式 =======================================================================
    #ax2 = figobj.add_axes(rect_2, axis_bgcolor='black')
    #ax2.set_axisbelow(True)  # 网格线放在底层
    '''
    # ==== 改变坐标线的颜色 ==============================================================================
    for child in ax2.get_children():
        if isinstance(child, matplotlib.spines.Spine):
            child.set_color('lightblue')

    # =====得到 X 轴 和 Y 轴 的两个 Axis 对象 =============================================================
    xaxis_2 = ax2.get_xaxis()
    yaxis_2 = ax2.get_yaxis()
    ax2.set_axisbelow(True)  # 网格线放在底层

    # === 得到 X 轴 和 Y 轴 的两个 Axis 对象 =============================================================
    xaxis_2 = ax2.get_xaxis()
    yaxis_2 = ax2.get_yaxis()

    # === 设置两个坐标轴上的 grid ==========================================================================
    xaxis_2.grid(True, 'major', color='0.3', linestyle='solid', linewidth=0.2)
    xaxis_2.grid(True, 'minor', color='0.3', linestyle='dotted', linewidth=0.1)

    yaxis_2.grid(True, 'major', color='0.3', linestyle='solid', linewidth=0.2)
    yaxis_2.grid(True, 'minor', color='0.3', linestyle='dotted', linewidth=0.1)

    # === 设定 X 轴主要坐标点与辅助坐标点的样式 ==============================================================
    for malabel in ax2.get_xticklabels(minor=False):
        malabel.set_fontsize(2)
        malabel.set_horizontalalignment('right')
        malabel.set_rotation('45')

    for milabel in ax2.get_xticklabels(minor=True):
        milabel.set_fontsize(2)
        milabel.set_color('blue')
        milabel.set_horizontalalignment('right')
        milabel.set_rotation('45')

    # 第一只：设定 X 轴坐标的范围
    # ==================================================================================================================================================
    ax2.set_xlim(-1, length_x)
    '''
    '''
    #   第一只：设定 X 轴上的坐标
    # ==================================================================================================================================================
    df_data_list = []
    for date_string,row in df.iterrows():
        open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20 = row[:10]
        if volume > 0 :
            df_data_list.append(date_string)

    datelist = [datetime.date(int(ys), int(ms), int(ds)) for ys, ms, ds in
                [dstr.split('-') for dstr in df_data_list]]

    # 确定 X 轴的 MajorLocator
    mdindex = []  # 每个月第一个交易日在所有日期列表中的 index
    years = set([d.year for d in datelist])  # 所有的交易年份

    for y in sorted(years):
        months = set([d.month for d in datelist if d.year == y])  # 当年所有的交易月份
        for m in sorted(months):
            monthday = min([dt for dt in datelist if dt.year == y and dt.month == m])  # 当月的第一个交易日
            mdindex.append(datelist.index(monthday))

    xMajorLocator = FixedLocator(numpy.array(mdindex))

    # 第一只：确定 X 轴的 MinorLocator
    wdindex = {}  # value: 每周第一个交易日在所有日期列表中的 index; key: 当周的序号 week number（当周是第几周）

    for d in datelist:
        isoyear, weekno = d.isocalendar()[0:2]
        dmark = isoyear * 100 + weekno
        if dmark not in wdindex:
            wdindex[dmark] = datelist.index(d)

    xMinorLocator = FixedLocator(numpy.array(sorted(wdindex.values())))

    # 第一只：确定 X 轴的 MajorFormatter 和 MinorFormatter
    def x_major_formatter_2(idx, pos=None):
        return datelist[idx].strftime('%Y-%m-%d')

    def x_minor_formatter_2(idx, pos=None):
        return datelist[idx].strftime('%m-%d')

    xMajorFormatter = FuncFormatter(x_major_formatter_2)
    xMinorFormatter = FuncFormatter(x_minor_formatter_2)

    # 第一只：设定 X 轴的 Locator 和 Formatter
    xaxis_2.set_major_locator(xMajorLocator)
    xaxis_2.set_major_formatter(xMajorFormatter)

    xaxis_2.set_minor_locator(xMinorLocator)
    xaxis_2.set_minor_formatter(xMinorFormatter)

    # 第一只：设定 X 轴主要坐标点与辅助坐标点的样式
    for malabel in ax2.get_xticklabels(minor=False):
        malabel.set_fontsize(2)
        malabel.set_horizontalalignment('right')
        malabel.set_rotation('45')

    for milabel in ax2.get_xticklabels(minor=True):
        milabel.set_fontsize(2)
        milabel.set_color('blue')
        milabel.set_horizontalalignment('right')
        milabel.set_rotation('45')

    # 第一只：设定成交量 Y 轴坐标的范围
    # ==================================================================================================================================================
    maxvol = df['volume'].max()  # 注意是 int 类型
    ax2.set_ylim(0, maxvol)

    #   第一只：设定成交量 Y 轴上的坐标
    # ==================================================================================================================================================
    vollen = len(str(maxvol))

    volstep_pri = int(round(maxvol / 10.0 + 5000, -4))

    yMajorLocator_2 = MultipleLocator(volstep_pri)

    # 第一只：确定 Y 轴的 MajorFormatter
    #dimsuffix = u'股' #u'元' if u'成交额' in pdata else u'股'

    def y_major_formatter_2(num, pos=None):
        if num >= 10 ** 8:  # 大于 1 亿
            return (str(round(num / 10.0 ** 8, 2)) + u'亿' ) if num != 0 else '0'
        else:
            return (str(num / 10.0 ** 4) + u'万' ) if num != 0 else '0'

    # def y_major_formatter_2(num, pos=None):
    #       return int(num)
    yMajorFormatter_2 = FuncFormatter(y_major_formatter_2)

    # 确定 Y 轴的 MinorFormatter
    #   def y_minor_formatter_2(num, pos=None):
    #       return int(num)
    #   yMinorFormatter_2= FuncFormatter(y_minor_formatter_2)
    yMinorFormatter_2 = NullFormatter()

    # 第一只：设定 X 轴的 Locator 和 Formatter
    yaxis_2.set_major_locator(yMajorLocator_2)
    yaxis_2.set_major_formatter(yMajorFormatter_2)

    #   yaxis_2.set_minor_locator(yMinorLocator_2)
    yaxis_2.set_minor_formatter(yMinorFormatter_2)

    # 第一只：设定 Y 轴主要坐标点与辅助坐标点的样式
    for malab in ax2.get_yticklabels(minor=False):
        malab.set_font_properties(__font_properties__)
        malab.set_fontsize(3)  # 这个必须放在前一句后面，否则作用会被覆盖
    '''
    '''
    # 第一只：成交量数值在图中间的显示
    # ==================================================================================================================================================
    for iy in range(volstep_pri, int(maxvol), volstep_pri):
        for ix in mdindex[1:-1:3]:
            newlab = ax2.text(ix + 8, iy, y_major_formatter_2(iy))
            newlab.set_font_properties(__font_properties__)
            newlab.set_color('0.3')
            newlab.set_fontsize(2)
            newlab.set_zorder(0)  # XXX: 放在底层
            #   newlab.set_verticalalignment('center')
    '''


    # ==================================================================================================================================================
    # =======    XXX: K 线图部分
    # ==================================================================================================================================================

    # ==== 添加 Axes 对象 ============================================================================
    #ax1 = figobj.add_axes(rect_1, axis_bgcolor='black', sharex=ax2)
    '''
    axes_1_sec = ax1.twinx()
    #   axes_1_sec.set_axisbelow(True)  # 网格线放在底层

    axes_1_sec.set_yscale('log', basey=expbase)  # 使用对数坐标

    #   得到 X 轴 和 Y 轴 的两个 Axis 对象
    # ==================================================================================================================================================
    xaxis_1_sec = axes_1_sec.get_xaxis()
    yaxis_1_sec = axes_1_sec.get_yaxis()

    ax1.set_axisbelow(True)  # 网格线放在底层
    ax1.set_yscale('log', basey=expbase)  # 使用对数坐标

    # ====改变坐标线的颜色 =============================================================================
    for child in ax1.get_children():
        if isinstance(child, matplotlib.spines.Spine):
            child.set_color('lightblue')

    # === 得到 X 轴 和 Y 轴 的两个 Axis 对象 ===========================================================
    xaxis_1 = ax1.get_xaxis()
    yaxis_1 = ax1.get_yaxis()

    # 设定 X 轴坐标的范围
    # ==================================================================================================================================================
    axes_1_sec.set_xlim(-1, length_x)

    #   先设置 label 位置，再将 X 轴上的坐标设为不可见。因为与 成交量子图 共用 X 轴
    # ==================================================================================================================================================

    # 设定 X 轴的 Locator 和 Formatter
    xaxis_1_sec.set_major_locator(xMajorLocator)
    xaxis_1_sec.set_major_formatter(xMajorFormatter)

    xaxis_1_sec.set_minor_locator(xMinorLocator)
    xaxis_1_sec.set_minor_formatter(xMinorFormatter)

    # 将 X 轴上的坐标设为不可见。
    for malab in axes_1_sec.get_xticklabels(minor=False):
        malab.set_visible(False)

    for milab in axes_1_sec.get_xticklabels(minor=True):
        milab.set_visible(False)

    # 设定 Y 轴坐标的范围
    # ==================================================================================================================================================
    #axes_1_sec.set_ylim(ylowlim_price, #* open_price_sec / open_price_pri,
    #                    yhighlim_price) # * open_price_sec / open_price_pri)

    #   设定 Y 轴上的坐标
    # ==================================================================================================================================================

    #   主要坐标点
    # ----------------------------------------------------------------------------
    yticks_major_sec = []
    ylowlim_price_sec = ylowlim_price  #* open_price_sec / open_price_pri
    yhighlim_price_sec = yhighlim_price #* open_price_sec / open_price_pri

    for i in range(1, 999):
        newloc = ylowlim_price_sec * (expbase ** i)
        if newloc <= yhighlim_price_sec:
            yticks_major_sec.append(newloc)
        else:
            break

    yMajorLocator_1_sec = FixedLocator(numpy.array(yticks_major_sec))

    # 确定 Y 轴的 MajorFormatter
    def y_major_formatter_1_sec(num, pos=None):
        return str(round(num / 1000.0, 2))

    yMajorFormatter_1_sec = FuncFormatter(y_major_formatter_1_sec)

    # 设定 X 轴的 Locator 和 Formatter
    yaxis_1_sec.set_major_locator(yMajorLocator_1_sec)
    yaxis_1_sec.set_major_formatter(yMajorFormatter_1_sec)
    '''

    # 设定 Y 轴主要坐标点与辅助坐标点的样式
    #for mal in axes_1_sec.get_yticklabels(minor=False):
    #    mal.set_fontsize(6)

    '''
    # 辅助坐标点
    # ----------------------------------------------------------------------------
    yticks_minor_sec = []
    mtstart_sec = ylowlim_price_sec * (1.0 + (expbase - 1.0) / 2)
    for i in range(999):
        newloc = mtstart_sec * (expbase ** i)
        if newloc <= yhighlim_price_sec:
            yticks_minor_sec.append(newloc)
        else:
            break
    '''

    #yMinorLocator_1_sec = FixedLocator(numpy.array(yticks_minor_sec))  # XXX minor ticks 已经在上面一并设置，这里不需要了。

    # 确定 Y 轴的 MinorFormatter
    #def y_minor_formatter_1_sec(num, pos=None):
    #    return str(round(num / 1000.0, 2))

    #yMinorFormatter_1_sec = FuncFormatter(y_minor_formatter_1_sec)

    # 设定 X 轴的 Locator 和 Formatter
    #yaxis_1_sec.set_minor_locator(yMinorLocator_1_sec)
    #yaxis_1_sec.set_minor_formatter(yMinorFormatter_1_sec)
    # 设定 Y 轴主要坐标点与辅助坐标点的样式
    #for mal in axes_1_sec.get_yticklabels(minor=True):
    #    mal.set_fontsize(5)
    #    mal.set_color('blue')


    #fig, (ax1,ax2) = plt.subplots(2,1, sharex=True,edgecolor = 'k') #facecolor='k')
    #fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
    #figobj.subplots_adjust(wspace=None, hspace=0.0001, top=0.9, bottom=0.1, left=0.2, right=0.98)
    plt.subplots_adjust(wspace=None, hspace=0.0001, top=0.9, bottom=0.1, left=0.2, right=0.98)

    ax1.set_title(name + '  ' + code, fontproperties=zhfont, fontsize =10 ,fontweight = 5)

    #fig.subplots_adjust(bottom=0.2)
    #for ax in ax1,ax2:
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])
    ax1.xaxis.set_major_locator(mondays)
    ax1.xaxis.set_minor_locator(alldays)

    #ax.yaxis.set_major_formatter()
    #ax2.xaxis.set_major_formatter(mondayFormatter)
    #ax2.annotate('buttom',xy=(0,4),xytext=(0.2,0.2),arrowprops=dict(facecolor='blue', shrink=0.05))
    #ax2.figsize(4,2)

    #plt.style.use('dark_background')

    # ax.xaxis.set_back_color('b')
    #ax.xaxis.gridLineColor('r')


    #ax.add_line(df['ma5']) #.plot(color='c')


    ax1.xaxis_date()
    ax2.xaxis_date()
    ax1.autoscale_view()
    ax2.autoscale_view()

    #plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    ax1.grid(True)
    #win_path = os.getcwd()

    #plt.title.set_fontsize(16)
    plt.show()
