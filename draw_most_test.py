# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 09:36:06 2018

@author: 123
"""

import tushare as ts
# import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import sys
sys.setrecursionlimit(5000)


TOKEN = '56c554861c29f507bb46a6514e00355d8bda337ece83f416fe728043'
START_DATE = '20180101'
END_DATE = '20181030'
CODE = '600609.SH'
ts.set_token(TOKEN)
pro = ts.pro_api()
filepath = "C:\\Users\\123\\Desktop\\core_stocks.txt"


def get_code_list():
    data = pd.read_table(filepath, header=None, encoding='gb2312',
                         delim_whitespace=True, index_col=0)
    tdx = []
    for s in data.index:
        if len(str(s)) == 6:
            tdx.append(str(s) + '.SZ')
        elif len(str(s)) > 6:
            tdx.append(str(s)[-6:] + '.SH')
        else:
            tdx.append(str(s).zfill(6) + '.SZ')
    return tdx


def get_data(code=CODE):
    df = pro.daily(ts_code=code, start_date=START_DATE, end_date=END_DATE)
    factor = pro.adj_factor(ts_code=code, start_date=START_DATE,
                            end_date=END_DATE)
    factor = factor[factor.trade_date.isin(df.trade_date)]
    df = pd.merge(df, factor, how='left', on='trade_date')
    df['fac'] = df.adj_factor/df.adj_factor[0]
    df['adj_close'] = df.close * df.fac
    df.drop(['open', 'high', 'low', 'pre_close', 'change', 'pct_change', 'vol',
             'amount'], axis=1, inplace=True)
    df.sort_values("trade_date", inplace=True, ascending=True)
    return df


def draw_most(capital_date, capital_list):
    df = pd.DataFrame({'date': capital_date, 'capital': capital_list})
    df['d2max'] = df.capital.expanding().max()
    df['d2here'] = 1 - df['capital']/df['d2max']
    temp = df.sort_values(by=['d2here'], ascending=False)
    draw_max = round(temp.iloc[0].d2here, 3)
    # draw_max = str(draw_max*100) + '%'
    end_date = temp.iloc[0].date
    temp_here = df[df.date < end_date]
    start_date = temp_here.sort_values(by=['capital'],
                                       ascending=False).iloc[0].date
    print('最大回撤：{}, 开始日期：{}, 结束日期：{}'.format(draw_max,
          start_date, end_date))
    return draw_max, start_date, end_date


def up_most(capital_date, capital_list):
    df = pd.DataFrame({'date': capital_date, 'capital': capital_list})
    df['d2min'] = df.capital.expanding().min()
    df['d2here'] = df['capital']/df['d2min'] - 1
    temp = df.sort_values(by=['d2here'], ascending=False)
    up_max = round(temp.iloc[0].d2here, 3)
    end_date = temp.iloc[0].date
    temp_here = df[df.date < end_date]
    start_date = temp_here.sort_values(by=['capital'],
                                       ascending=True).iloc[0].date
    print(f'最大涨幅：{up_max}, 开始日期： {start_date}, 结束日期： {end_date}')
    return up_max, start_date, end_date


if __name__ == "__main__":
    tdx_code = get_code_list()
    draw_max, start_date, end_date = [], [], []
    up_max = []
    for cd in tdx_code:
        df = get_data(code=cd)
        print(f'股票代码：{cd}')
        temp = draw_most(df.trade_date, df.adj_close)
        up_max.append(up_most(df.trade_date, df.adj_close)[0])
        draw_max.append(temp[0])
        start_date.append(temp[1])
        end_date.append(temp[2])
    res = [('code', tdx_code), ('draw_max', draw_max), ('up_max', up_max),
           ('start_date', start_date), ('end_date', end_date)]
    result = pd.DataFrame.from_dict(dict(res))
    result.to_csv('C:\\Users\\123\\Desktop\\pyintaller\\my.csv')
'''
df = pro.daily(trade_date=END_DATE)
df2 = pro.daily(trade_datle='20181026')
df = pd.merge(df, df2, how='inner', on='ts_code')
'''
