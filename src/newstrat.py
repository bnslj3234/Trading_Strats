#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 20:06:53 2023

@author: bnsl.j3
"""
"""Shivam Goel: So we will take short term and long term tenor..
We will go long if 
1) price is above 20-sma in long term tenor
2) price is above 20-sma in short term tenor on closing basis or during the candle if above 20-sma + ATR
3) we will stop out if price is below 13-sma of short tenor candle on closing basis or intra-candle if price is below 13-sma - ATR..
[16/01, 17:58] Shivam Goel: Short term tenor=5 minute
Long term tenor = daily or 75 minute candle"""


import pandas as pd
import numpy as np
import datetime
import datetime as dt
import math
import zipfile
from tqdm import tqdm
from datetime import timedelta

def get_future_prices(expiry_date):
    month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+expiry_date[-2:] +"/"+ pd.to_datetime(expiry_date , format = '%d-%m-%Y').strftime("%d%m%Y") +"_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    df_weekly_futures.set_index("Time", inplace = True)
    # df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
    return df_weekly_futures

def get_folder_name(expiry_date):
    if pd.to_datetime(expiry_date, format ="%d-%m-%Y")>=pd.to_datetime("01-02-2022", format ="%d-%m-%Y"):
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/Options'+'/'
    else:
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
    return folder_name, folder_name_

def make_candle_data(df_weekly_futures_prices , candle_freq_min):
    # df_weekly_futures = get_future_prices(date)
    # df_weekly_futures_prices = (df_w1eekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
    df_weekly_futures_prices = df_weekly_futures_prices.reset_index()
    time_temp=pd.read_csv("TimeTemplate.csv", index_col = 0)
    df_weekly_futures_prices=df_weekly_futures_prices.drop_duplicates(["Time"])
    df_weekly_futures_prices.set_index("Time", inplace = True)
    # time_temp.set_index("Time", inplace = True)
    # time_temp["Call_LTP"] = df_call_option["LTP"]
    time_temp["Avg_Fut_Price"] = df_weekly_futures_prices
    time_temp.index = pd.to_datetime(time_temp.index,errors='coerce')
    
    bars = time_temp["Avg_Fut_Price"].resample(candle_freq_min).ohlc()
    bars.index = pd.to_datetime(bars.index,errors='coerce').strftime("%H:%M:%S")
    bars = bars.shift(1).dropna()
    bars["SMA_Close_"+str(period)] = bars["close"].rolling(period).mean()
    # bars = SuperTrend(bars)1
    time_temp=time_temp.fillna(method="bfill")
    time_temp.index = pd.to_datetime(time_temp.index,errors='coerce').strftime("%H:%M:%S")
    bars["Avg_Fut_Price"] = df_weekly_futures_prices
    bars = ATR(bars, period, ohlc=ohlc)
    # bars = pd.concat([bars,time_temp], axis = 1)
    # bars = bars.join(time_temp)
    # bars.to_csv("../res/"+df_call_option["Ticker"][0][:-4]+"_"+df_put_option["Ticker"][0][:-4]+"_STR_Calculation2.csv")
    return bars

def ATR(df, period, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute Average True Range (ATR)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR)
            ATR (ATR_$period)
    """
    atr = 'ATR_' + str(period)

    # Compute true range only if it is not computed and stored earlier in the df
    if not 'TR' in df.columns:
        df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
        df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
        df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

        df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)
        df['TR'].iloc[0] = np.nan
        # df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    df = EMA(df, 'TR', atr, period, alpha=False)

    return df

def EMA(df, base, target, period, alpha=False):
    """
    Function to compute Exponential Moving Average (EMA)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the EMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles
        alpha : Boolean if True indicates to use the formula for computing EMA using alpha (default is False)

    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """
    df[target] = np.nan
    # df[target].iloc[period] = df[base][1:(period+1)].mean()
    con = pd.concat([df[1:(period+1)][base].rolling(window=period).mean(), df[period+1:][base]])

    if (alpha == True):
        # (1 - alpha) * previous_val + alpha * current_val where alpha = 1 / period
        df[target] = con.ewm(alpha=1 / period, adjust=False).mean()
    else:
        # ((current_val - previous_val) * coeff) + previous_val where coeff = 2 / (period + 1)
        df[target] = con.ewm(span=period, adjust=False).mean()

    df[target].fillna(0, inplace=True)
    return df
# add  stoploss
date_details = pd.read_csv("Backtest_Dates_Mondays.csv", header = 0).dropna()
date_list = date_details["Date"].tolist()
# holidays_list = pd.read_csv("HolidayList.csv")
# Thur_Hols = holidays_list["Date"][holidays_list["Day"] == "Thursday"].tolist()
# Wed_hol = holidays_list["Date"][holidays_list["Day"] == "Wednesday"].tolist()
# wed_thu_hol = holidays_list[(holidays_list["Day"] == "Thursday") | (holidays_list["Day"] == "Wednesday")]["Date"].tolist()
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'/Users/bnsl.j3/Desktop/Jatin Bansal/Options/BankNifty Output/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path = "/Users/bnsl.j3/Desktop/Jatin Bansal/Options/"
# instrument ="BANKNIFTY"
long_candle_freq_min = "15min"
short_candle_freq_min = "5min"
period = 20
# # instrument ="NIFTY"
# if instrument =="BANKNIFTY":
#     roundoff_factor = 100
#     start_time ="09:25:01"
#     end_time ="15:00:00"
#     last_trade_open_time ="14:45:00"
#     contract_size = 25
#     # prefix ="BN"
#     # spot_file_name ="BANKNIFTY.csv"
# elif instrument =="NIFTY":
#     roundoff_factor = 50
#     start_time ="09:20:00"
#     end_time ="15:25:00"
#     last_trade_open_time ="15:00:00"
#     contract_size = 50
    
# extra_fraction = 0.05
# percent_based_offset = False
# premium_based_offset = True
# call_premium = 100
# put_premium = 100
# discount_premium = 15
# buy_put_hedge = True
# buy_call_hedge = True
# stoploss_fraction = 0.3
# individual_stoploss_fraction = 1
# check_individual_stoploss = False
# check_stoploss = False
# extra_offset = 500
transactionbook = [["Trade_Start_date", "Date_name","expiry_date", "start_time", "future_price", "Call_Ticker", "Put_Ticker",
                    "Start_ATM_IV", "call_sell_price", "put_sell_price","Hedge_Call_Ticker", "Hedge_Put_Ticker","Hedge_Call_Buy_Price","Hedge_Put_Buy_Price","OTM2_Call_Ticker", "OTM2_Put_Ticker","OTM2_Call_Sell_Price","OTM2_Put_Sell_Price","OTM3_Call_Ticker", "OTM3_Put_Ticker","OTM3_Call_Buy_Price","OTM3_Put_Buy_Price", "stop_date", "stop_date_name", "end_time",
                    "future_price_end","End_ATM_IV", "call_buy_price", "put_buy_price","Hedge_Call_Sell_Price","Hedge_Put_Sell_Price","OTM2_Call_Buy_Price","OTM2_Put_Buy_Price","OTM3_Call_Sell_Price","OTM3_Put_Sell_Price","min_profit","max_profit","Till_Date_Min","Till_Date_Max","trade_type",]]

date_list = ['05-02-2021',
'01-07-2022',
'08-07-2022',
'15-07-2022',
'22-07-2022','15-07-2022']
# ,"05-02-2021", "12-02-2021","19-02-2021"
# profit_tracker = pd.DataFrame(columns = date_list)
# date_list = ['15-07-2022']
combined_short_tenor =pd.DataFrame()
combined_long_tenor =pd.DataFrame()
active_long_position = False
active_short_position = False
for date in tqdm(date_list):
    df_weekly_futures = get_future_prices(date)
    df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
    long_tenor = make_candle_data(df_weekly_futures_prices,long_candle_freq_min)
    long_tenor["SMA_Close_"+str(period)] = long_tenor["close"].rolling(period).mean()
    # long_tenor.index = date+" "+long_tenor.index
    short_tenor = make_candle_data(df_weekly_futures_prices,short_candle_freq_min) 
    short_tenor_ATR = ATR(short_tenor, period)
    short_tenor["SMA_Close_"+str(period)] = short_tenor["close"].rolling(period).mean()
    # short_tenor.index = date+" "+short_tenor.index
    # combined_long_tenor = pd.concat([combined_long_tenor,long_tenor])
    # combined_short_tenor = pd.concat([combined_short_tenor,short_tenor])
    
# combined_long_tenor.index = pd.to_datetime(combined_long_tenor.index)
# combined_short_tenor.index = pd.to_datetime(combined_short_tenor.index)
    '''Long Position'''
    for index in time_temp.index.tolist():
        if long_tenor["Avg_Fut_Price"][index] > long_tenor["SMA_Close_"+str(period)][index] | :
            print("Long Position")
        if long_tenor["Avg_Fut_Price"][index] > short_tenor["SMA_Close_"+str(period)][index]  + short_tenor["ATR_"+str(period)][index]
            print("Long Position")
        if fafsdf:
            print("Square Off Long Position")
            
    