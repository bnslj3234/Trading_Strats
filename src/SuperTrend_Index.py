# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:53:21 2022

@author: Jatin
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from datetime import timedelta
from dateutil.relativedelta import relativedelta, TH, WE
import datetime as dt
import os
import math
import zipfile
from tqdm import tqdm

def get_folder_name(expiry_date):
    if pd.to_datetime(expiry_date, format ="%d-%m-%Y")>=pd.to_datetime("01-02-2022", format ="%d-%m-%Y"):
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/Options'+'/'
    else:
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
    return folder_name, folder_name_

def get_next_day(date, get_day):
    # today_ = datetime()
    date_ = pd.to_datetime(date, format = "%d-%m-%Y")
    if get_day == 'T':
        thursday = date_ + dt.timedelta( (3-date_.weekday()) % 7 )
        return thursday.strftime("%d-%m-%Y")
    if get_day == 'W':
        wednesday = date_ + dt.timedelta( (2-date_.weekday()) % 7 )
        return wednesday.strftime("%d-%m-%Y")

def get_last_day(date, get_day):
    end_of_month = pd.to_datetime(date, format ="%d-%m-%Y") + relativedelta(day=31)
    if get_day == "T":
        last_thursday = end_of_month + relativedelta(weekday=TH(-1))
        return last_thursday.strftime("%d-%m-%Y")
    elif get_day == 'W':
        last_wednesday = end_of_month + relativedelta(weekday=WE(-1))
        
def get_expiry_date(date_str,typee):
    if typee == "W":
        if get_next_day(date_str, 'T') in Thur_Hols:
            expiry_date = get_next_day(date_str, 'W')
        else:
            expiry_date = get_next_day(date_str, 'T')
        return expiry_date
    elif typee == "M":
        if pd.to_datetime(get_next_day(date_str, 'T'), format ="%d-%m-%Y").strftime("%B") == pd.to_datetime(date_str, format ="%d-%m-%Y").strftime("%B"):
            if get_last_day(date_str, 'T') in Thur_Hols:
                expiry_date = get_last_day(date_str, 'W')
            else:
                expiry_date = get_last_day(date_str, 'T')
            return expiry_date
        else:
            next_m_weekly_expiry = get_next_day(date_str, 'T')
            if get_last_day(next_m_weekly_expiry, 'T') in Thur_Hols:
                expiry_date = get_last_day(next_m_weekly_expiry, 'W')
            else:
                expiry_date = get_last_day(next_m_weekly_expiry, 'T')
            return expiry_date
        
def get_future_prices(expiry_date):
    month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+expiry_date[-2:] +"/"+ pd.to_datetime(expiry_date , format = '%d-%m-%Y').strftime("%d%m%Y") +"_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    # df_weekly_futures.set_index("Time", inplace = True)
    # df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
    return df_weekly_futures

def get_expiry_date(date_str):
    
    if get_next_day(date_str, 'T') in Thur_Hols:
        expiry_date = get_next_day(date_str, 'W')
    else:
        expiry_date = get_next_day(date_str, 'T')
    return expiry_date
    
def check_stoploss(entry_price,current_price, position, stop_loss_percent):
    if position == "Long":
        if current_price < (1-stop_loss_percent)*entry_price:
            return True
        else:
            return False
        
    elif position == "Short":
        if current_price > (1+stop_loss_percent)*entry_price:
            return True
        else:
            return False
        
def profit_booking1(current_future_price,sell_price,profit_booking_points,call_put_flag):
    # current_future_price,sell_price,profit_booking_points,call_put_flag = 33622.35, 33618.55, 70, 'P'
    if((current_future_price > (sell_price+profit_booking_points)) & (call_put_flag == "P")):
        return True
    elif((current_future_price < (sell_price-profit_booking_points)) & (call_put_flag == "C")):
        return True
    else:
        return False

def trailing_stoploss_normal(current_future_price,max_value_till,trailing_stoploss_points,call_put_flag):
    if ((current_future_price > (max_value_till+trailing_stoploss_points)) & (call_put_flag == "C")):
        # print("CALL Trailing Stoploss HIT",str(current_future_price), str(max_value_till),str(trailing_stoploss_points), str(call_put_flag))
        return True
    elif ((current_future_price < (max_value_till-trailing_stoploss_points)) & (call_put_flag == "P")):
        # print("PUT Trailing Stoploss HIT" ,str(current_future_price), str(max_value_till),str(trailing_stoploss_points), str(call_put_flag))
        return True 
    else:
        return False
    
def traling_stoploss(current_future_price,max_value_till,future_price,trailing_stoploss_points,call_put_flag,sl_points):
    if((call_put_flag == "C") & ((future_price - current_future_price) <= (revised_stoploss_points - trailing_stoploss_points))):
        curr_sl_points = max(trailing_stoploss_points, trailing_stoploss_points + (future_price - current_future_price))
    elif((call_put_flag == "P")&((current_future_price - future_price) <= (revised_stoploss_points - trailing_stoploss_points))):
        curr_sl_points = max(trailing_stoploss_points, trailing_stoploss_points + (current_future_price - future_price))
    # if(abs(future_price - current_future_price) <= abs(revised_stoploss_points - trailing_stoploss_points)):
    #     if(call_put_flag == "C"):
    #         curr_sl_points = max(trailing_stoploss_points, trailing_stoploss_points + (future_price - current_future_price))
    #     elif(call_put_flag == "P"):
    #         curr_sl_points = max(trailing_stoploss_points, trailing_stoploss_points + (current_future_price - future_price))
    else:
        # print("curr_sl_points : ",revised_stoploss_points,current_future_price,max_value_till,future_price,call_put_flag,sl_points )
        curr_sl_points = revised_stoploss_points
    sl_points = max(sl_points, curr_sl_points)
    # if(((max_value_till - current_future_price) < max(-1*trailing_stoploss_points,(max_value - current_future_price - revised_stoploss_points))) & (call_put_flag == "C")):
    #     return True
    # if(((current_future_price - max_value_till) < max(-1*trailing_stoploss_points,(max_value - current_future_price- revised_stoploss_points))) & (call_put_flag == "P")):
    #     return True
    if ((current_future_price > (max_value_till+sl_points)) & (call_put_flag == "C")):
        print(current_future_price,max_value_till,future_price,call_put_flag,sl_points)
        # print("CALL Trailing Stoploss HIT",str(current_future_price), str(max_value_till),str(trailing_stoploss_points), str(call_put_flag))
        return True,sl_points
    elif ((current_future_price < (max_value_till-sl_points)) & (call_put_flag == "P")):
        print(current_future_price,max_value_till,future_price,call_put_flag,sl_points)
        # print("PUT Trailing Stoploss HIT" ,str(current_future_price), str(max_value_till),str(trailing_stoploss_points), str(call_put_flag))
        return True ,sl_points
    # if ((current_future_price > (max_value_till+trailing_stoploss_points)) & (call_put_flag == "C")):
    #     # print("CALL Trailing Stoploss HIT",str(current_future_price), str(max_value_till),str(trailing_stoploss_points), str(call_put_flag))
    #     return True
    # elif ((current_future_price < (max_value_till-trailing_stoploss_points)) & (call_put_flag == "P")):
    #     # print("PUT Trailing Stoploss HIT" ,str(current_future_price), str(max_value_till),str(trailing_stoploss_points), str(call_put_flag))
    #     return True 
    else:
        return False, sl_points
    
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
        df[target] = con.ewm(alpha=1 / period, adjust=False).mean()

    df[target].fillna(0, inplace=True)
    return df

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
    EMA(df, 'TR', atr, period, alpha=False)

    return df

def SuperTrend(df, period = 10, multiplier=3, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute SuperTrend

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR), ATR (ATR_$period)
            SuperTrend (ST_$period_$multiplier)
            SuperTrend Direction (STX_$period_$multiplier)
    """

    ATR(df, period, ohlc=ohlc)
    atr = 'ATR_' + str(period)
    st = 'ST' #+ str(period) + '_' + str(multiplier)
    stx = 'STX' #  + str(period) + '_' + str(multiplier)

    """
    SuperTrend Algorithm :

        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR

        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND)) 
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)

        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                            Current FINAL LOWERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                    Current FINAL UPPERBAND
    """

    # Compute basic upper and lower bands
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
                                                         df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
                                                         df['final_lb'].iat[i - 1]

    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[
            i] <= df['final_ub'].iat[i] else \
            df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] > \
                                     df['final_ub'].iat[i] else \
                df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] >= \
                                         df['final_lb'].iat[i] else \
                    df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] < \
                                             df['final_lb'].iat[i] else 0.00

        # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down', 'up'), np.NaN)
    # df[stx].iloc[0] = 'down'
    # Remove basic and final bands from the columns
    # df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb','TR', atr], inplace=True, axis=1)

    df.fillna(0, inplace=True)
    return df


def make_candle_data(df_fut, candle_freq_min):
    # df_fut = df_weekly_futures
    time_temp=pd.read_csv("TimeTemplate.csv")
    # df_put_option=df_put_option.drop_duplicates(["Time"]).reset_index()
    # df_put_option.set_index("Time", inplace = True)
    # df_call_option=df_call_option.drop_duplicates(["Time"]).reset_index()
    # df_call_option.set_index("Time", inplace = True)
    # df_put_option=df_put_option.drop_duplicates(["Time"]).reset_index()
    df_fut=df_fut.drop_duplicates(["Time"]).reset_index()
    df_fut.set_index("Time", inplace = True)
    # df_put_option.set_index("Time", inplace = True)
    time_temp.set_index("Time", inplace = True)
    time_temp["FUT_B"] = df_fut["FUT_B"]
    time_temp["FUT_S"] = df_fut["FUT_S"]
    time_temp.index = pd.to_datetime(time_temp.index,errors='coerce')
    bars = time_temp.FUT_B.resample(candle_freq_min).ohlc()
    bars.index = pd.to_datetime(bars.index,errors='coerce').strftime("%H:%M:%S")
    bars = bars.shift(1).dropna()
    bars = SuperTrend(bars)
    time_temp.index = pd.to_datetime(time_temp.index).strftime("%H:%M:%S")
    time_temp["STX"] = bars["STX"]
    
    time_temp=time_temp.fillna(method="ffill")
    # bars=bars.fillna(method="ffill")
    bars.to_csv("../res/"+"STR_Calculation_Index_"+date+".csv")

    return time_temp

def get_data(df_fut,df_put_option, df_call_option):
    # df_fut = df_weekly_futures
    # df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    # df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    time_temp=pd.read_csv("TimeTemplate.csv")
    df_put_option=df_put_option.drop_duplicates(["Time"]).reset_index()
    df_call_option=df_call_option.drop_duplicates(["Time"]).reset_index()
    df_call_option.set_index("Time", inplace = True)
    df_put_option.set_index("Time", inplace = True)
    time_temp.set_index("Time", inplace = True)
    df_fut = df_fut.set_index("Time")
    time_temp["Call_BuyPrice"] = df_call_option["BuyPrice"]
    time_temp["Put_BuyPrice"] = df_put_option["BuyPrice"]
    time_temp["Call_SellPrice"] = df_call_option["SellPrice"]
    time_temp["Put_SellPrice"] = df_put_option["SellPrice"]
    time_temp["FUT_S"] = df_fut["FUT_S"]
    time_temp=time_temp.fillna(method="bfill")
    time_temp = time_temp.fillna(0)
    return time_temp

candle_freq_min = "3min"
supertrend_period = 10
supertrend_multiplier=3

stoploss_percent = 0.16
stoploss_percent_combined = 0.01
instrument = "BANKNIFTY"
otm_value_wed_thu = 0
expiry_freq = 'W'
check_combined_stoploss = False
check_individual_stoploss = False
trailing_stoploss_points = 100
revised_stoploss_points = 200
trailing_stop_loss = True
profit_booking = False
profit_booking_points = 70
sl_points = 0
# instrument = "NIFTY"
if instrument == "BANKNIFTY":
    roundoff_factor = 100
    start_time = "09:18:00"
    end_time = "15:24:00"
    contract_size = 25
    # prefix = "BN"
    # spot_file_name = "BANKNIFTY.csv"
elif instrument == "NIFTY":
    roundoff_factor = 50
    start_time = "09:44:00"
    end_time = "14:41:00"
    contract_size = 50


start_time_dt = datetime.datetime.strptime(start_time, "%H:%M:%S").time()
end_time_dt=datetime.datetime.strptime(end_time,"%H:%M:%S").time()

date_list = pd.read_csv("Backtest_Dates.csv", header = 0)["Date"].dropna().tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] == "Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] == "Wednesday"].tolist()
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'E:/BankNifty Output/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path ="E:/"

# date_list = ["01-02-2021","02-02-2021","03-02-2021","04-02-2021","05-02-2021","08-02-2021"]
# transactions_book = [["Date", 'Day',"Time","FuturesPrice","Ref_FuturePrice","vix",'Upper_Band2','Upper_Band1','Lower_Band1','Lower_Band2','Instrument_NameL', 'BuyPriceL','BuyQtyL','Instrument_NameS', 'SellPriceS', 'SellQtyS', 'SellPriceL','SellQtyL','BuyPriceS','BuyQtyS',"Profit","trade_type"]]
transactions_book = [['Date','Day',"Call_Instrument","Put_Instrument",'Time', 'Future', 'ATM Strike',
       'CallStrike','PutStrike', 'Call_Sell', 
       'Put_Sell','Call Buy', 'Call PNL','Put Buy', 'Put PNL', 
       'Trade_Type_Call','Trade_Type_Put', "Max_Value"]]
# date_list = ["02-11-2021", "03-11-2021", "08-11-2021", "09-11-2021"]
# date_list = ["04-03-2022"]
date_list = ['31-08-2021']

# '25-03-2021','26-03-2021',
# ,"02-11-2021", "02-11-2021", "03-11-2021", "08-11-2021", "09-11-2021", "10-11-2021"]
qty = 0
max_value = 0
previous_signal = ''
for date in date_list:
    print(date)
    folder_name, folder_name_ = get_folder_name(date)
    month_name=pd.to_datetime(date, format = "%d-%m-%Y").strftime("%B")
    date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    dir_1=changing_path + date[-4:] + "/" + month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    to_zip=dir_1+folder_name[:-1]+str(".zip")

    zf = zipfile.ZipFile(to_zip)
    '''read Futures file for that day. took future's price as of start_time to calculate ATM'''
    
    df_weekly_futures = get_future_prices(date)
    wfut_cols = [x for x in df_weekly_futures.columns if"WFUT"in x]
    df_weekly_futures=df_weekly_futures.fillna(method="bfill")
    bars_call_put_data = make_candle_data(df_weekly_futures, candle_freq_min)

    '''Get expiry date and then get file for both and call option for their respective Strike price'''
    expiry_date = get_expiry_date(date)    
    expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
    
    max_loss = int(180000*stoploss_percent_combined/25)
    # max_loss = 72
    
    position_active_call = False
    position_active_put = False
    buy_put_price = 0
    buy_call_price = 0
    sell_price_put = 0
    sell_price_call = 0
    # sq_off_type_C = 'Start_Trade_C'
    # sq_off_type_P = 'Start_Trade_P'
    # transactions_book.append([date,date_name,start_time,future_price,working_strike,call_strike,put_strike,sell_price_call,sell_price_put,combined_premium,np.nan,np.nan,np.nan,np.nan,sq_off_type_C,sq_off_type_P])
    # trade_active = True
    # print(len(df_rel_call_option), len(df_rel_put_option))
    # print(call_file_name[:-8] ," Call Sold : ", sell_price_call, put_file_name[:-8], " Put Sold : ", sell_price_put, " at Time : ", start_time)
    
    # bars_call_put_data["Call_plus_Put"] = bars_call_put_data["Put_SellPrice"] + bars_call_put_data["Call_SellPrice"]
    
    for index_ in tqdm(bars_call_put_data[(bars_call_put_data.index >= start_time) & (bars_call_put_data.index <= end_time)].index):

        if (qty == 0):
            if((bars_call_put_data["STX"][index_] == 'up') & (previous_signal!= 'up')):
                future_price = df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0]
                working_strike = round(future_price / roundoff_factor) * roundoff_factor
                call_strike = working_strike + otm_value_wed_thu
                put_strike = working_strike - otm_value_wed_thu
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                
                call_put_data = get_data(df_weekly_futures,df_put_option, df_call_option)
                # if call_put_data["FUT_S"][index_] == 0.0:
                #     break
                initial_investment = (working_strike)*0.2*2
                index_p  = index_
                idx_p = np.searchsorted(call_put_data.index, index_)
                sell_price_put = call_put_data["Put_BuyPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = True
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_P = 'SuperTrend_P_Sell'
                max_value = future_price
                sl_points = trailing_stoploss_points
                # sl_points = trailing_stoploss_points
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,future_price,working_strike,call_strike,put_strike,np.nan,sell_price_put,np.nan,np.nan,np.nan,np.nan,np.nan,sq_off_type_P,max_value])
                qty = -1
                previous_signal = bars_call_put_data["STX"][index_]
                print(max_value)
                # print("Qty : " + str(qty) + "PUT Sell")
                
            if((bars_call_put_data["STX"][index_] == 'down')& (previous_signal!= 'down')):
                future_price = df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0]               
                working_strike = round(future_price / roundoff_factor) * roundoff_factor
                call_strike = working_strike + otm_value_wed_thu
                put_strike = working_strike - otm_value_wed_thu
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                
                call_put_data = get_data(df_weekly_futures,df_put_option, df_call_option)
                # if call_put_data["FUT_S"][index_] == 0.0:
                #     break
                initial_investment = (working_strike)*0.2*2
                
                index_c  = index_
                idx_c = np.searchsorted(call_put_data.index, index_)
                sell_price_call = call_put_data["Call_BuyPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = True
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_c+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'SuperTrend_C_Sell'
                max_value = future_price
                sl_points = trailing_stoploss_points
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,future_price,working_strike,call_strike,put_strike,sell_price_call,np.nan,np.nan,np.nan,np.nan,np.nan,sq_off_type_C,np.nan,max_value])
                qty = -1
                previous_signal = bars_call_put_data["STX"][index_]
                print(max_value)
                # print("Qty : " + str(qty) + "CALL Sell")
        elif(qty!=0):
            # print(date, qty,bars_call_put_data["STX"][index_])
            # if((position_active_call == True) & s):
            #     index_c  = index_
            #     idx_c = np.searchsorted(call_put_data.index, index_)
            #     buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
            #     position_active_call = False
            #     # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
            #     sq_off_type_C = 'SuperTrend_C_Buy_Stoploss'
            #     transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan])
            #     qty = 0
            if (position_active_call == True):
                tsp_hit, sl_points = traling_stoploss(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points, "C",sl_points)
                # print(tsp_hit, sl_points , "C")
            if (position_active_put == True):
                tsp_hit, sl_points = traling_stoploss(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points, "P",sl_points)
                # print(tsp_hit, sl_points, "P")
            # traling_stoploss(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points, "C")
            # traling_stoploss(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points, "P")
            if(((bars_call_put_data["STX"][index_] == 'up') & (position_active_call == True))):
                '''Square_Off_Previous'''
                index_c  = index_
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'SuperTrend_C_Buy_SC'
                qty = 0
                max_value = 0
                
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan,max_value])
                
                # print("Signal Change to "+bars_call_put_data["STX"][index_]+"Qty : " + str(qty) + "PUT BuyBAck")
                '''Start_New_Trade'''
                future_price = df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0]               
                working_strike = round(future_price / roundoff_factor) * roundoff_factor
                call_strike = working_strike + otm_value_wed_thu
                put_strike = working_strike - otm_value_wed_thu
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                
                call_put_data = get_data(df_weekly_futures,df_put_option, df_call_option)
                # if call_put_data["FUT_S"][index_] == 0.0:
                #     break
                initial_investment = (working_strike)*0.2*2
                index_p  = index_
                idx_p = np.searchsorted(call_put_data.index, index_)
                sell_price_put = call_put_data["Put_BuyPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = True
                max_value = future_price
                sl_points = trailing_stoploss_points
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_P = 'SuperTrend_P_Sell_SC'
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,future_price,working_strike,call_strike,put_strike,np.nan,sell_price_put,np.nan,np.nan,np.nan,np.nan,np.nan,sq_off_type_P,max_value])
                qty = -1
                previous_signal = bars_call_put_data["STX"][index_]
                print(max_value)
                # print("Signal Change to "+bars_call_put_data["STX"][index_]+"Qty : " + str(qty) + "CALL SELL on signal change")
                
            elif(((bars_call_put_data["STX"][index_] == 'down') & (position_active_put == True))):
                '''Square_Off_Previous'''
                index_p  = index_
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_P = 'SuperTrend_P_Buy_SC'
                qty = 0
                max_value = 0
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P,max_value])
                
                # print("Signal Change to "+bars_call_put_data["STX"][index_]+"Qty : " + str(qty) + "CALL BuyBAck")
                '''Start_New_Trade'''
                future_price = df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0]               
                working_strike = round(future_price / roundoff_factor) * roundoff_factor
                call_strike = working_strike + otm_value_wed_thu
                put_strike = working_strike - otm_value_wed_thu
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                
                call_put_data = get_data(df_weekly_futures,df_put_option, df_call_option)
                # if call_put_data["FUT_S"][index_] == 0.0:
                #     break
                initial_investment = (working_strike)*0.2*2
                index_c  = index_
                idx_c = np.searchsorted(call_put_data.index, index_)
                sell_price_call = call_put_data["Call_BuyPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = True
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_c+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'SuperTrend_C_Sell_SC'
                max_value = future_price
                sl_points = trailing_stoploss_points
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,future_price,working_strike,call_strike,put_strike,sell_price_call,np.nan,np.nan,np.nan,np.nan,np.nan,sq_off_type_C,np.nan,max_value])
                qty = -1
                previous_signal = bars_call_put_data["STX"][index_]
                print(max_value)
                # print("Signal Change to "+bars_call_put_data["STX"][index_]+"Qty : " + str(qty) + "PUT SELL on signal change")

                
            elif((check_individual_stoploss == True) & (call_put_data["Call_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_call) & (position_active_call == True)):
                index_c  = index_
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                # buy_put_price = df_rel_put_option["C"][df_rel_put_option["C"]["Time"] == df_rel_call_option["Time"][i]]
                position_active_call = False
                # max_loss =  max_loss + (sell_price_call-buy_call_price)
                # print("Stop loss hit for call bought call option buying at : ",call_put_data.index[min(idx_c+1, len(call_put_data)-1)], " for : ",buy_call_price , " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'Stoploss_C'
                qty = 0
                previous_signal = bars_call_put_data["STX"][index_]
                # print("Qty : " + str(qty) + "CALL BuyBAck on Stoploss Call Price")
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan,max_value])

            elif((check_individual_stoploss == True) & (call_put_data["Put_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_put) & (position_active_put == True)):
                index_p  = index_
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                # max_loss =  max_loss + (sell_price_put-buy_put_price)
                # print("Stop loss hit for put bought put option buying at : ",call_put_data.index[min(idx_p+1, len(call_put_data)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price) )            
                sq_off_type_P = 'Stoploss_P'
                qty = 0
                max_value = 0
                sl_points = trailing_stoploss_points
                previous_signal = bars_call_put_data["STX"][index_]
                # print("Qty : " + str(qty) + "PUT BuyBAck on Stoploss PUT Price")
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P,max_value])
            
            elif((tsp_hit) & (position_active_put == True) & (trailing_stop_loss == True)):
            # elif(traling_stoploss(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points,"P") & (position_active_put == True) & (trailing_stop_loss == True)):
                # print("")
                print(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points,"P", "TP")
                index_p  = index_
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_P = 'TStoploss_P'
                qty = 0
                max_value = 0
                sl_points = trailing_stoploss_points
                previous_signal = bars_call_put_data["STX"][index_]
                # print("Qty : " + str(qty) + "PUT BuyBAck on Stoploss Index Price")
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P,max_value])
                # break
            # print("CALL : " + str(traling_stoploss(call_put_data["FUT_S"][index_],max_value,trailing_stoploss_points,"C") + str(position_active_call)))
            elif((tsp_hit) & (position_active_call == True)& (trailing_stop_loss == True)):                
            # elif(traling_stoploss(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points, "C") & (position_active_call == True)& (trailing_stop_loss == True)):                
                # print("Qty : " + str(qty) + "CALL BuyBAck on Stoploss Index Price")
                print(call_put_data["FUT_S"][index_],max_value,future_price,trailing_stoploss_points, "C", "TC")
                index_c  = index_
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'TStoploss_C'
                qty = 0
                max_value = 0
                sl_points = trailing_stoploss_points
                previous_signal = bars_call_put_data["STX"][index_]
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan,max_value])
                # break
            
            elif(profit_booking1(call_put_data["FUT_S"][index_],future_price,profit_booking_points,"C") & ((position_active_call == True) & (profit_booking == True))):
                index_c  = index_
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'ProfitBook_C'
                qty = 0
                max_value = 0
                sl_points = trailing_stoploss_points
                previous_signal = bars_call_put_data["STX"][index_]
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan,max_value])
                
            elif( profit_booking1(call_put_data["FUT_S"][index_],future_price,profit_booking_points,"P") & ((position_active_put == True)& (profit_booking == True))):
                index_p  = index_
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_P = 'ProfitBook_P'
                qty = 0
                max_value = 0
                sl_points = trailing_stoploss_points
                previous_signal = bars_call_put_data["STX"][index_]
                # print("Qty : " + str(qty) + "PUT BuyBAck on Stoploss Index Price")
                transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P,max_value])
                
            # elif(((sell_price_call - call_put_data["Call_SellPrice"][index_]) <= -1*max_loss) & (position_active_put == False) & (check_combined_stoploss == True) &(position_active_call == True)):
            #     index_c  = index_
            #     idx_c = np.searchsorted(call_put_data.index, index_)
            #     buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
            #     position_active_call = False
            #     # print("combine Stop loss hit for call option buying at : ",call_put_data.index[min(idx_c+1, len(call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
            #     sq_off_type_C = 'CombinedSL_C'
            #     qty = 0
            #     transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan])

                
            # elif(((sell_price_put - call_put_data["Put_SellPrice"][index_]) <= -1*max_loss) & (position_active_call == False) & (check_combined_stoploss == True) &(position_active_put == True)):
            #     index_p  = index_
            #     idx_p = np.searchsorted(call_put_data.index, index_)
            #     buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
            #     position_active_put = False
            #     qty = 0
            #     # print("combine Stop loss hit for put option buying at : ",call_put_data.index[min(idx_p+1, len(call_put_data)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price))
            #     sq_off_type_P = 'CombinedSL_P'
            #     transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P])
            # print("PUT : " + str(traling_stoploss(call_put_data["FUT_S"][index_],max_value,trailing_stoploss_points,"P") + str(position_active_put)))
            if (position_active_call == True):
                # print(max_value)
                max_value = min(max_value,call_put_data["FUT_S"][index_])
                # print(max_value , "C")
            if (position_active_put == True):
                # print(max_value,"P")
                max_value = max(max_value,call_put_data["FUT_S"][index_])
                # print(max_value, "P")
                
            if(index_ == end_time):
                if(position_active_put == True):
                    index_p  = index_
                    idx_p = np.searchsorted(call_put_data.index, index_)
                    buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                    position_active_put = False
                    # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                    sq_off_type_P = 'EndTime_P_Buy'
                    qty = 0
                    max_value = 0
                    sl_points = trailing_stoploss_points
                    previous_signal = ''
                    # print("Qty : " + str(qty) + "PUT BuyBAck on EndTime")
                    transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P,max_value])
                if(position_active_call == True):
                    index_c  = index_
                    idx_c = np.searchsorted(call_put_data.index, index_)
                    buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                    position_active_call = False
                    # print("SuperTrend hit for call option buying at : ",bars_call_put_data.index[min(idx_p+1, len(bars_call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                    sq_off_type_C = 'EndTime_C_Buy'
                    qty = 0
                    max_value = 0
                    sl_points = trailing_stoploss_points
                    previous_signal = ''
                    # print("Qty : " + str(qty) + "CALL BuyBAck on EndTime")
                    transactions_book.append([date,date_name,call_file_name[:-8],put_file_name[:-8],index_,df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == index_].values[0],working_strike,call_strike,put_strike,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan,max_value])
            
            
day_profit_df = pd.DataFrame(transactions_book[1:], columns = transactions_book[0])
cols = ['Date',
 'Day',"Call_Instrument","Put_Instrument",
 'Time',
 'Future',
 'ATM Strike',
 'CallStrike',
 'PutStrike',
 'Call_Sell',
 'Call Buy',
 'Call PNL',
 'Put_Sell',
 'Put Buy',
 'Put PNL',
 'Trade_Type_Call',
 'Trade_Type_Put']
day_profit_df = day_profit_df[cols]
day_profit_df.to_csv("../res/SuperTrend_Index_Output1.csv", index = False)