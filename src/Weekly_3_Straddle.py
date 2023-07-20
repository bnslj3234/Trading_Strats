#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 19:59:36 2023

@author: bnsl.j3
"""

import pandas as pd
import numpy as np
import datetime
# import matplotlib.pyplot as plt
# from datetime import timedelta
# from dateutil.relativedelta import relativedelta, TH, WE
import datetime as dt
import os
# import math
import zipfile
import warnings
from tqdm import tqdm

warnings.filterwarnings('ignore')
os.chdir("/Users/bnsl.j3/Desktop/Jatin Bansal/Options/OptionsCode/src")

def get_next_day(date, get_day):
    date_ = pd.to_datetime(date, format = "%d-%m-%Y")
    if get_day == 'T':
        thursday = date_ + dt.timedelta( (3-date_.weekday()) % 7 )
        return thursday.strftime("%d-%m-%Y")
    if get_day == 'W':
        wednesday = date_ + dt.timedelta( (2-date_.weekday()) % 7 )
        return wednesday.strftime("%d-%m-%Y")

def get_expiry_date(date):
    if get_next_day(date, 'T') in Thur_Hols:
        expiry_date = get_next_day(date, 'W')
    else:
        expiry_date = get_next_day(date, 'T')
    
    return expiry_date
        
def get_data(df_put_option, df_call_option):
    time_temp=pd.read_csv("TimeTemplate.csv")
    df_put_option=df_put_option.drop_duplicates(["Time"]).reset_index()
    df_call_option=df_call_option.drop_duplicates(["Time"]).reset_index()
    df_call_option.set_index("Time", inplace = True)
    df_put_option.set_index("Time", inplace = True)
    time_temp.set_index("Time", inplace = True)
    time_temp["Call_BuyPrice"] = df_call_option["BuyPrice"]
    time_temp["Put_BuyPrice"] = df_put_option["BuyPrice"]
    time_temp["Call_SellPrice"] = df_call_option["SellPrice"]
    time_temp["Put_SellPrice"] = df_put_option["SellPrice"]
    time_temp=time_temp.fillna(method="ffill")
    return time_temp

def get_future_prices(expiry_date):
    month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+expiry_date[-2:] +"/"+ pd.to_datetime(expiry_date , format = '%d-%m-%Y').strftime("%d%m%Y") +"_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    return df_weekly_futures

def get_folder_name(expiry_date):
    if pd.to_datetime(expiry_date, format ="%d-%m-%Y")>=pd.to_datetime("01-02-2022", format ="%d-%m-%Y"):
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/Options'+'/'
    else:
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
    return folder_name, folder_name_

def make_candle_data_option_premium(df_put_option ,df_call_option, candle_freq_min):
    # df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    # df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    time_temp=pd.read_csv("TimeTemplate.csv")
    df_put_option=df_put_option.drop_duplicates(["Time"]).reset_index()
    df_call_option=df_call_option.drop_duplicates(["Time"]).reset_index()
    df_call_option.set_index("Time", inplace = True)
    df_put_option.set_index("Time", inplace = True)
    time_temp.set_index("Time", inplace = True)
    time_temp["Call_LTP"] = df_call_option["LTP"]
    time_temp["Put_LTP"] = df_put_option["LTP"]
    time_temp["Combined_LTP"] = time_temp["Put_LTP"] + time_temp["Call_LTP"]
    time_temp.index = pd.to_datetime(time_temp.index,errors='coerce')
    
    bars = time_temp.Combined_LTP.resample(candle_freq_min).ohlc()
    bars.index = pd.to_datetime(bars.index,errors='coerce').strftime("%H:%M:%S")
    bars = bars.shift(1).dropna()
    # bars = SuperTrend(bars)
    time_temp=time_temp.fillna(method="bfill")
    time_temp.index = pd.to_datetime(time_temp.index,errors='coerce').strftime("%H:%M:%S")
    bars = bars.join(time_temp)
    # bars.to_csv("../res/"+df_call_option["Ticker"][0][:-4]+"_"+df_put_option["Ticker"][0][:-4]+"_STR_Calculation2.csv")
    return bars

def make_candle_data_index(combined_fut_prices, candle_freq_min):
    
    combined_fut_prices.index = pd.to_datetime(combined_fut_prices.index,errors='coerce')
    
    bars = combined_fut_prices.Avg_Fut_Price.resample(candle_freq_min).ohlc()
    # bars.index = pd.to_datetime(bars.index,errors='coerce').strftime("%H:%M:%S")
    bars = bars.shift(1).dropna()
    return bars

def RSI(data, window=7, adjust=False):
    # data = bars_future_data
    delta = data['close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()

    gains[gains < 0] = 0
    loss[loss > 0] = 0

    gain_ewm = gains.ewm(com=window - 1, adjust=adjust).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=adjust).mean())

    RS = gain_ewm / loss_ewm
    RSI = 100 - 100 / (1 + RS)

    return RSI

def EMA(df, base, target, period, alpha=False):
    # df, base, target = bars, "close", period + "_EMA"
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
    # df["RSI"]
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

def get_straddle_prices(zf1,folder_name_,instrument,pivot_strike,expiry_date,time,price_type):
    # zf1,time,price_type = zf,start_time, "SELL"
    expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
    pivot_put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(pivot_strike)+str("PE.NFO.csv")
    pivot_call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(pivot_strike)+str("CE.NFO.csv")
    df_put_option = pd.read_csv(zf1.open(folder_name_ + pivot_put_file_name))
    df_call_option = pd.read_csv(zf1.open(folder_name_+pivot_call_file_name))
    time_temp = get_data(df_put_option, df_call_option)
    if price_type.upper() == "SELL":
        pivot_call_price = time_temp["Call_BuyPrice"].loc[time]
        pivot_put_price = time_temp["Put_BuyPrice"].loc[time]
        # return pivot_call_price,pivot_put_price
    elif price_type.upper() == "BUY":
        pivot_call_price = time_temp["Call_SellPrice"].loc[time]
        pivot_put_price = time_temp["Put_SellPrice"].loc[time]
    
    return pivot_call_price,pivot_put_price,pivot_call_file_name[:-10],pivot_put_file_name[:-10]

def both_position_status(type_):
    if type_.upper() == "CLOSED":
        return False, False
    if type_.upper() == "OPEN":
        return True, True
    
def initiate_min_max_profits():  
    return 100000000,-100000000,100000000,-100000000
# def swap_information(position, information_type):
#     if information_type.upper() == "Price":
#         if position.upper() == "PIVOT":
#             return pivot_call_sell_price,pivot_put_sell_price
#         if position.upper() == "SUPPORT":
#             return support_call_sell_price,support_put_sell_price
#         if position.upper() == "RESISTANCE":
#             return resistance_call_sell_price,resistance_put_sell_price
#     elif information_type.upper() == "STRIKE":
#         if position.upper() == "PIVOT":
#             return pivot_strike
#         if position.upper() == "SUPPORT":
#             return support_strike
#         if position.upper() == "RESISTANCE":
#             return resistance_strike
#     elif information_type.upper() == "MAX_MIN_PROFIT":
#         if position.upper() == "PIVOT":
#             return pivot_min_profit,pivot_max_profit
#         if position.upper() == "SUPPORT":
#             return support_min_profit,support_max_profit
#         if position.upper() == "RESISTANCE":
#             return resistance_min_profit,resistance_max_profit
        
def get_previous_week_fut_ohlc(date):

    combined_df = pd.DataFrame()
    for dayss in range(1,8):
        week_date = (pd.to_datetime(date, format ="%d-%m-%Y") + datetime.timedelta(days=-1*dayss)).strftime("%d%m%Y")
        month_name=pd.to_datetime(week_date, format ="%d%m%Y").strftime("%B")
        try:
            weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+week_date[-2:] +"/"+ week_date +"_results.csv"
            df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
            df_weekly_futures["New_Index"] = pd.to_datetime(week_date , format = '%d%m%Y').strftime("%d-%m-%Y") + " " +df_weekly_futures["Time"]
            df_weekly_futures["New_Index"] = pd.to_datetime(df_weekly_futures["New_Index"], format="%d-%m-%Y %H:%M:%S")
            df_weekly_futures.set_index("New_Index", inplace = True)
            combined_df = pd.concat([combined_df,df_weekly_futures.iloc[:,7]])
            
        except:
            # print("Date Not Present in Folder " + week_date +" " +pd.to_datetime(week_date, format ="%d%m%Y" ).strftime("%A"))
            df_weekly_futures = pd.DataFrame()
    
    combined_df.sort_index(inplace=True)
    combined_df.sort_index().dropna(inplace=True)
    high = combined_df.max().values[0]
    low = combined_df.min().values[0]
    openn = combined_df.iloc[0][0]
    close = combined_df.iloc[-1][0]
    
    return openn, high, low, close
    
    
# add  stoploss
date_details = pd.read_csv("Updated_MondayList.csv", header = 0).dropna(axis = 1)
date_list = date_details["Date"].tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] == "Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] == "Wednesday"].tolist()
# wed_thu_hol = holidays_list[(holidays_list["Day"] == "Thursday") | (holidays_list["Day"] == "Wednesday")]["Date"].tolist()
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'/Users/bnsl.j3/Desktop/Jatin Bansal/Options/BankNifty Output/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path = "/Users/bnsl.j3/Desktop/Jatin Bansal/Options/"
instrument ="BANKNIFTY"

# instrument ="NIFTY"
if instrument =="BANKNIFTY":
    roundoff_factor = 100
    start_time ="09:35:00"
    end_time ="15:15:00"
    last_trade_open_time ="14:45:00"
    contract_size = 25
    # prefix ="BN"
    # spot_file_name ="BANKNIFTY.csv"
elif instrument =="NIFTY":
    roundoff_factor = 50
    start_time ="09:27:00"
    end_time ="15:15:00"
    last_trade_open_time ="15:00:00"
    contract_size = 50

transaction_cost_percent_sell = 0.1125
transaction_cost_percent_buy = 0.05
critical_point_check = '15min'

pivot_call_position_active = False
pivot_put_position_active = False

support_call_position_active = False
support_put_position_active = False

resistance_call_position_active = False
resistance_put_position_active = False

transactions_book = [['Date', 'Day', 'Trade_Time', 'Weekly_Future_Price', "Position_Type","Signal_Type", "Trade_Type",
                      "Put_Strike",'Put_Name',"Put_Price",
                      "Call_Strike", 'Call_Name', "Call_Price", "Call_Profit","Put_Profit","Min_Call_Profit","Max_Call_Profit","Min_Put_Profit","Max_Put_Profit"]]
# "Min_Total_Profit","Max_Total_Profit","Call_Min_Profit", "Call_Max_Profit", "Put_Min_Profit", "Put_Max_Profit"
# [date,date_name,index_, future_price, working_strike,
#        call_strike,put_strike, put_file_name[:-8], 
#        ,put_sell_price, put_buy_price, 
#        trade_type_entry,trade_type_exit]
# date_list = ['01-07-2022']
# date_list = ['26-07-2022', '27-07-2022']
# print(date)
# date = '27-12-2021'
# doubtful_dates = ['19-03-2021','05-02-2021','17-06-2022','01-04-2022','08-07-2022','11-03-2022']

# date_list = list(set(date_list) - set(doubtful_dates))

'''New Monday Dates'''
date_list.remove('08-02-2021')
date_list.remove('01-03-2021')
date_list.remove('24-05-2021')
date_list.remove('09-08-2021')
date_list.remove('20-09-2021')
date_list.remove('01-11-2021')
date_list.remove('29-11-2021')
date_list.remove('13-12-2021')
date_list.remove('20-12-2021')
date_list.remove('28-02-2022')
date_list.remove('07-03-2022')
date_list.remove('04-04-2022')
date_list.remove('10-01-2022')
date_list.remove('14-03-2022')

date_list.remove('28-06-2021')



# 1423
# Max/min atm pivot sum. change at every shift. Limit max/min
# adjustment if market openend at gap
# 1.) Run the existing code.
# 2.) Shift the entire strikes by the gap difference.
# 3.) Hedge Buying.
# 4.) cap it to 1.3x Pivot Total.
for date in (date_list):
    print(date)
    S1_hit = False
    S2_hit = False
    R1_hit = False
    R2_hit = False
    
    folder_name, folder_name_ = get_folder_name(date)
    month_name=pd.to_datetime(date, format = "%d-%m-%Y").strftime("%B")
    date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    dir_1=changing_path + date[-4:] + "/" + month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    to_zip=dir_1+folder_name[:-1]+str(".zip")
    zf = zipfile.ZipFile(to_zip)
    expiry_date = get_expiry_date(date)
    
    current_Date_index = date_list.index(date)
    df_weekly_futures = get_future_prices(date)
    df_weekly_futures=df_weekly_futures.fillna(method="ffill").set_index("Time")
    wfut_cols = [x for x in df_weekly_futures.columns if"WFUT"in x]
    fp_price = df_weekly_futures[wfut_cols[0]].loc[start_time]
    
    between_days = [(pd.to_datetime(date, format ="%d-%m-%Y") + datetime.timedelta(days=1*dayss)) for dayss in range(0,7)]
    between_days = [b for b in between_days if b.strftime("%A") not in ["Saturday", "Sunday", "Friday"]]
    between_days = [b.strftime("%d-%m-%Y") for b in between_days if b.strftime("%d-%m-%Y") not in holidays_list["Date"].tolist()]
    # end_date = between_days[-1]
    previous_open,previous_high,previous_low,previous_close = get_previous_week_fut_ohlc(date)
    
    pp = (previous_close + previous_high + previous_low)/3
    # use previous week's monday to friday from high low and close
    gap_diff = fp_price - pp
    R1 = (2*pp) - previous_low 
    S1 = (2*pp) - previous_high
    R2 = pp + (previous_high - previous_low) 
    S2 = pp - (previous_high - previous_low)
    R3 = previous_high + 2*(pp - previous_low)
    S3 = previous_low - 2*(previous_high - pp)
    
    # print(pp, R1,S1,R2,S2,R3,S3)
    pivot_strike = round(pp / roundoff_factor) * roundoff_factor
    support_strike = round(((S1+S2)*0.5 + gap_diff) / roundoff_factor) * roundoff_factor
    resistance_strike = round(((R1+R2)*0.5 + gap_diff) / roundoff_factor) * roundoff_factor
    # print(pivot_strike,support_strike,resistance_strike)
    
    pivot_call_sell_price,pivot_put_sell_price,pivot_call_file_name, pivot_put_file_name = get_straddle_prices(zf,folder_name_,instrument,pivot_strike,expiry_date,start_time, "SELL")
    support_call_sell_price,support_put_sell_price,support_call_file_name, support_put_file_name = get_straddle_prices(zf,folder_name_,instrument,support_strike,expiry_date,start_time, "SELL")
    resistance_call_sell_price,resistance_put_sell_price,resistance_call_file_name, resistance_put_file_name = get_straddle_prices(zf,folder_name_,instrument,resistance_strike,expiry_date,start_time, "SELL")

    pivot_trade_type= "Start_Time"
    support_trade_type = "Start_Time"
    resistance_trade_type = "Start_Time"
    
    transactions_book.append([date, date_name, start_time,fp_price , "Pivot","SELL", pivot_trade_type,
                          pivot_strike,pivot_put_file_name,pivot_put_sell_price,
                          pivot_strike, pivot_call_file_name, pivot_call_sell_price, np.nan, np.nan, np.nan])
    transactions_book.append([date, date_name, start_time,fp_price , "Support","SELL", support_trade_type,
                          support_strike,support_put_file_name,support_put_sell_price,
                          support_strike, support_call_file_name, support_call_sell_price, np.nan, np.nan, np.nan])
    transactions_book.append([date, date_name, start_time,fp_price , "Resistance","SELL", resistance_trade_type,
                          resistance_strike,resistance_put_file_name,resistance_put_sell_price,
                          resistance_strike, resistance_call_file_name, resistance_call_sell_price, np.nan, np.nan, np.nan])
    
    pivot_call_position_active,pivot_put_position_active = both_position_status("Open")    
    support_call_position_active,support_put_position_active = both_position_status("Open")
    resistance_call_position_active,resistance_put_position_active = both_position_status("Open")
    
    total_call_min_profit,total_call_max_profit,total_put_min_profit,total_put_max_profit = initiate_min_max_profits()
    total_min_profit, total_max_profit = 1000000,-1000000
    call_pivot_min_profit,call_pivot_max_profit,put_pivot_min_profit,put_pivot_max_profit = initiate_min_max_profits()   
    call_resistance_min_profit,call_resistance_max_profit,put_resistance_min_profit,put_resistance_max_profit = initiate_min_max_profits()   
    call_support_min_profit,call_support_max_profit,put_support_min_profit,put_support_max_profit = initiate_min_max_profits()   

    max_sum_premium = pivot_call_sell_price +pivot_put_sell_price+support_call_sell_price +support_put_sell_price+resistance_call_sell_price +resistance_put_sell_price
    '''Check Stoploss for in between dates'''
    # print(between_days)
    profit_list = []
    start_time_t = start_time
    
    for stop_date in tqdm(between_days):
        if ((pivot_call_position_active == False) & (pivot_put_position_active == False)):
            break
        # print(stop_date)
        folder_name, folder_name_ = get_folder_name(stop_date)
        month_name=pd.to_datetime(stop_date, format ="%d-%m-%Y").strftime("%B")
        dir_1=changing_path + stop_date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(stop_date[-4:]) + '/'
        stop_date_name = pd.to_datetime(stop_date, format ="%d-%m-%Y").strftime("%A")
        to_zip=dir_1+folder_name[:-1]+str(".zip")
        zf1 = zipfile.ZipFile(to_zip)
        new_expiry_date = get_expiry_date(stop_date)
        expiry_month_name=pd.to_datetime(new_expiry_date, format = "%d-%m-%Y").strftime("%B")
        
        df_weekly_futures_daily = get_future_prices(stop_date)
        df_weekly_futures_daily.set_index("Time", inplace=True)
        wfut_cols = [x for x in df_weekly_futures_daily.columns if"WFUT"in x]
        df_weekly_futures_daily = df_weekly_futures_daily.rename(columns = {wfut_cols[0]:"Future_Price"})
        df_weekly_futures_daily.index = pd.to_datetime(df_weekly_futures_daily.index)
        df_weekly_futures_daily = df_weekly_futures_daily.Future_Price.resample(critical_point_check).ohlc()
        df_weekly_futures_daily.index = df_weekly_futures_daily.index.strftime("%H:%M:%S")
        
        for index_t in (df_weekly_futures_daily[start_time:end_time].index):
            # profit = 200000
            # stop_loss = 100000
            current_fp_price = df_weekly_futures_daily["close"].loc[index_t]
            
            # try:
            pivot_call_buy_price,pivot_put_buy_price,pivot_call_file_name, pivot_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,pivot_strike,new_expiry_date,index_t, "BUY")
            support_call_buy_price,support_put_buy_price,support_call_file_name, support_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,support_strike,new_expiry_date,index_t, "BUY")
            resistance_call_buy_price,resistance_put_buy_price,resistance_call_file_name, resistance_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,resistance_strike,new_expiry_date,index_t, "BUY")
                    
            call_pivot_profit = (pivot_call_sell_price - pivot_call_buy_price) 
            put_pivot_profit = (pivot_put_sell_price - pivot_put_buy_price)
            put_resistance_profit = (resistance_put_sell_price - resistance_put_buy_price)
            call_resistance_profit = (resistance_call_sell_price - resistance_call_buy_price)
            put_support_profit = (support_put_sell_price - support_put_buy_price)
            call_support_profit = (support_call_sell_price - support_call_buy_price)
            
            total_profit = call_pivot_profit+put_pivot_profit+put_resistance_profit+call_resistance_profit+put_support_profit+call_support_profit
            total_call_profit = call_pivot_profit+call_resistance_profit+call_support_profit
            total_put_profit = put_pivot_profit+put_resistance_profit++put_support_profit

            total_min_profit= min(total_min_profit,total_profit)
            total_max_profit= max(total_max_profit,total_profit)
            # total_min_profit,total_max_profit,total_call_min_profit,total_call_max_profit,total_put_min_profit,total_put_max_profit,
            total_call_min_profit = min(total_call_min_profit,total_call_profit)
            total_call_max_profit = max(total_call_max_profit,total_call_profit)
            total_put_min_profit = min(total_put_min_profit,total_put_profit)
            total_put_max_profit = max(total_put_max_profit,total_put_profit)
            
            call_pivot_min_profit = min(call_pivot_min_profit,call_pivot_profit)
            call_pivot_max_profit = max(call_pivot_max_profit,call_pivot_profit)
            call_resistance_min_profit = min(call_resistance_min_profit,call_resistance_profit)
            call_resistance_max_profit = max(call_resistance_max_profit,call_resistance_profit)
            call_support_min_profit = min(call_support_min_profit,call_support_profit)
            call_support_max_profit = max(call_support_max_profit,call_support_profit)
            
            put_pivot_min_profit = min(put_pivot_min_profit,put_pivot_profit)
            put_pivot_max_profit = max(put_pivot_max_profit,put_pivot_profit)
            put_resistance_min_profit = min(put_resistance_min_profit,put_resistance_profit)
            put_resistance_max_profit = max(put_resistance_max_profit,put_resistance_profit)
            put_support_min_profit = min(put_support_min_profit,put_support_profit)
            put_support_max_profit = max(put_support_max_profit,put_support_profit)
            
            """If index price goes above Resist1. Exit S1 and make new position at avg(r2,r3)"""
            if ((current_fp_price > R1) & (current_fp_price < R2) & (R1_hit == False)):
                R1_hit = True
                support_call_buy_price,support_put_buy_price,support_call_file_name, support_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,support_strike,new_expiry_date,index_t, "BUY")
                support_call_position_active,support_put_position_active = both_position_status("Closed")
                # print("Record Trade in Book")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support","BUY", "R1_Hit",
                                      support_strike,support_put_file_name,support_put_buy_price,support_strike,
                                      support_call_file_name,support_call_buy_price, call_support_profit,
                                      put_support_profit, call_support_min_profit, call_support_max_profit, 
                                      put_support_min_profit, put_support_max_profit])
                
                support_call_sell_price,support_put_sell_price = pivot_call_sell_price,pivot_put_sell_price
                support_call_file_name, support_put_file_name = pivot_call_file_name, pivot_put_file_name
                support_strike = pivot_strike
                call_support_profit,put_support_profit = call_pivot_profit,put_pivot_profit
                call_support_min_profit,call_support_max_profit = call_pivot_min_profit,call_pivot_max_profit
                put_support_min_profit,put_support_max_profit = put_pivot_min_profit,put_pivot_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Pivot-Support","Virtual_Change", "R1_Hit",
                                      support_strike,support_put_file_name,support_put_sell_price,support_strike,
                                      support_call_file_name,support_call_sell_price, call_support_profit,
                                      put_support_profit, call_support_min_profit, call_support_max_profit,
                                      put_support_min_profit, put_support_max_profit])
                

                pivot_call_sell_price,pivot_put_sell_price = resistance_call_sell_price,resistance_put_sell_price
                pivot_call_file_name, pivot_put_file_name = resistance_call_file_name, resistance_put_file_name
                pivot_strike = resistance_strike
                call_pivot_profit,put_pivot_profit = call_resistance_profit,put_resistance_profit
                call_pivot_min_profit,call_pivot_max_profit = call_resistance_min_profit,call_resistance_max_profit
                put_pivot_min_profit,put_pivot_max_profit = put_resistance_min_profit,put_resistance_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price,"Resistance-Pivot","Virtual_Change", "R1_Hit",
                                      pivot_strike,pivot_put_file_name,pivot_put_sell_price,
                                      pivot_strike,pivot_call_file_name,pivot_call_sell_price, call_pivot_profit,
                                      put_pivot_profit, call_pivot_min_profit, call_pivot_max_profit, 
                                      put_pivot_min_profit, put_pivot_max_profit])

                resistance_strike = round((R2+R3)*0.5 / roundoff_factor) * roundoff_factor
                resistance_call_sell_price,resistance_put_sell_price,resistance_call_file_name, resistance_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,resistance_strike,new_expiry_date,index_t, "SELL")
                resistance_call_position_active,resistance_put_position_active = both_position_status("Open")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Resistance","SELL", "R1_Hit",
                                      resistance_strike,resistance_put_file_name,resistance_put_sell_price,
                                      resistance_strike, resistance_call_file_name, resistance_call_sell_price, 
                                      np.nan, np.nan, np.nan])
                

                call_resistance_min_profit,call_resistance_max_profit,put_resistance_min_profit,put_resistance_max_profit = initiate_min_max_profits()   
            
            # """If index price goes above Resist2. Exit pivot and make new position at r3"""
            elif((current_fp_price > R2) & (R2_hit == False) & (R1_hit == True)):
                R2_hit = True
                support_call_buy_price,support_put_buy_price,support_call_file_name, support_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,support_strike,new_expiry_date,index_t, "BUY")
                support_call_position_active,support_put_position_active = both_position_status("Closed")
                # print("Record Trade in Book")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support","BUY", "R2_Hit",
                                      support_strike,support_put_file_name,support_put_buy_price,support_strike,
                                      support_call_file_name,support_call_buy_price, call_support_profit,
                                      put_support_profit, call_support_min_profit, call_support_max_profit,
                                      put_support_min_profit, put_support_max_profit])
                
                support_call_sell_price,support_put_sell_price = pivot_call_sell_price,pivot_put_sell_price
                support_call_file_name, support_put_file_name = pivot_call_file_name, pivot_put_file_name
                support_strike = pivot_strike
                call_support_profit,put_support_profit = call_pivot_profit,put_pivot_profit
                call_support_min_profit,call_support_max_profit = call_pivot_min_profit,call_pivot_max_profit
                put_support_min_profit,put_support_max_profit = put_pivot_min_profit,put_pivot_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Pivot-Support","Virtual_Change", "R2_Hit",
                                      support_strike,support_put_file_name,support_put_sell_price,support_strike,
                                      support_call_file_name,support_call_sell_price, call_support_profit,
                                      put_support_profit, call_support_min_profit, call_support_max_profit, 
                                      put_support_min_profit, put_support_max_profit])

                pivot_call_sell_price,pivot_put_sell_price = resistance_call_sell_price,resistance_put_sell_price
                pivot_call_file_name, pivot_put_file_name = resistance_call_file_name, resistance_put_file_name
                pivot_strike = resistance_strike
                call_pivot_profit,put_pivot_profit = call_resistance_profit,put_resistance_profit
                call_pivot_min_profit,call_pivot_max_profit = call_resistance_min_profit,call_resistance_max_profit
                put_pivot_min_profit,put_pivot_max_profit = put_resistance_min_profit,put_resistance_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Resistance-Pivot","Virtual_Change", "R1_Hit",
                                      pivot_strike,pivot_put_file_name,pivot_put_sell_price,pivot_strike,
                                      pivot_call_file_name,pivot_call_sell_price, call_pivot_profit,put_pivot_profit, 
                                      call_pivot_min_profit,call_pivot_max_profit, put_pivot_min_profit,put_pivot_max_profit])
                
                resistance_strike = round(R3 / roundoff_factor) * roundoff_factor
                resistance_call_sell_price,resistance_put_sell_price,resistance_call_file_name, resistance_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,resistance_strike,new_expiry_date,index_t, "SELL")
                resistance_call_position_active,resistance_put_position_active = both_position_status("Open")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Resistance","SELL", 
                                          "R2_Hit",resistance_strike,resistance_put_file_name,resistance_put_sell_price,
                                          resistance_strike, resistance_call_file_name, resistance_call_sell_price,
                                          np.nan, np.nan, np.nan])
                

                call_resistance_min_profit,call_resistance_max_profit,put_resistance_min_profit,put_resistance_max_profit = initiate_min_max_profits()   

                
            # """If index price goes below Support1 . Exit R1 and make new position at avg(s2,s3)"""
            elif ((current_fp_price < S1) & (current_fp_price > S2) & (S1_hit == False)):
                S1_hit = True
                resistance_call_buy_price,resistance_put_buy_price,resistance_call_file_name, resistance_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,resistance_strike,new_expiry_date,index_t, "BUY")
                resistance_call_position_active,resistance_put_position_active = both_position_status("Closed")
                # print("Record Trade in Book")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Resistance","BUY", 
                                          "S1_Hit",resistance_strike,resistance_put_file_name,resistance_put_buy_price,
                                      resistance_strike,resistance_call_file_name,resistance_call_buy_price, call_resistance_profit,put_resistance_profit, call_resistance_min_profit, call_resistance_max_profit, put_resistance_min_profit, put_resistance_max_profit])
                        
                resistance_call_sell_price,resistance_put_sell_price = pivot_call_sell_price,pivot_put_sell_price
                resistance_call_file_name, resistance_put_file_name = pivot_call_file_name, pivot_put_file_name
                resistance_strike = pivot_strike
                call_resistance_profit,put_resistance_profit = call_pivot_profit,put_pivot_profit
                call_resistance_min_profit,call_resistance_max_profit = call_pivot_min_profit,call_pivot_max_profit
                put_resistance_min_profit,put_resistance_max_profit = put_pivot_min_profit,put_pivot_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Pivot-Resistance","Virtual_Change", "R2_Hit",
                                      resistance_strike,resistance_put_file_name,resistance_put_sell_price,
                                      resistance_strike,resistance_call_file_name,resistance_call_sell_price, call_resistance_profit,put_resistance_profit, call_resistance_min_profit, call_resistance_max_profit, put_resistance_min_profit, put_resistance_max_profit])

                pivot_call_sell_price,pivot_put_sell_price = support_call_sell_price,support_put_sell_price
                pivot_call_file_name, pivot_put_file_name = support_call_file_name, support_put_file_name
                pivot_strike = support_strike
                call_pivot_profit,put_pivot_profit = call_support_profit,put_support_profit
                call_pivot_min_profit,call_pivot_max_profit = call_support_min_profit,call_support_max_profit
                put_pivot_min_profit,put_pivot_max_profit = put_support_min_profit,put_support_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support-Pivot","Virtual_Change", "R1_Hit",
                                      pivot_strike,pivot_put_file_name,pivot_put_sell_price,
                                      pivot_strike,pivot_call_file_name,pivot_call_sell_price, call_pivot_profit,put_pivot_profit, call_pivot_min_profit, call_pivot_max_profit, put_pivot_min_profit, put_pivot_max_profit])

                
                support_strike = round((S2+S3)*0.5 / roundoff_factor) * roundoff_factor
                support_call_sell_price,support_put_sell_price,support_call_file_name, support_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,support_strike,new_expiry_date,index_t, "SELL")
                support_call_position_active,support_put_position_active = both_position_status("Open")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support","SELL", "S1_Hit",
                          support_strike,support_put_file_name,support_put_sell_price,
                          support_strike, support_call_file_name, support_call_sell_price, np.nan, np.nan, np.nan])
   
                call_support_min_profit,call_support_max_profit,put_support_min_profit,put_support_max_profit = initiate_min_max_profits()   
            
            # """If index price goes below Support2 . Exit pivot and make new position at s3"""
            elif ((current_fp_price < S2) & (S2_hit == False) & (S1_hit == True)):
                S2_hit = True
                resistance_call_buy_price,resistance_put_buy_price,resistance_call_file_name, resistance_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,resistance_strike,new_expiry_date,index_t, "BUY")
                resistance_call_position_active,resistance_put_position_active = both_position_status("Closed")
                # print("Record Trade in Book")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Resistance","BUY", "S2_Hit",
                                      resistance_strike,resistance_put_file_name,resistance_put_buy_price,
                                      resistance_strike,resistance_call_file_name,resistance_call_buy_price, call_resistance_profit,put_resistance_profit, call_resistance_min_profit, call_resistance_max_profit, put_resistance_min_profit, put_resistance_max_profit])
                 
                resistance_call_sell_price,resistance_put_sell_price = pivot_call_sell_price,pivot_put_sell_price
                resistance_call_file_name, resistance_put_file_name = pivot_call_file_name, pivot_put_file_name
                resistance_strike = pivot_strike
                call_resistance_profit,put_resistance_profit = call_pivot_profit,put_pivot_profit
                call_resistance_min_profit,call_resistance_max_profit = call_pivot_min_profit,call_pivot_max_profit
                put_resistance_min_profit,put_resistance_max_profit = put_pivot_min_profit,put_pivot_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Pivot-Resistance","Virtual_Change", "R2_Hit",
                                      resistance_strike,resistance_put_file_name,resistance_put_sell_price,
                                      resistance_strike,resistance_call_file_name,resistance_call_sell_price, call_resistance_profit,put_resistance_profit, call_resistance_min_profit, call_resistance_max_profit, put_resistance_min_profit, put_resistance_max_profit])

                pivot_call_sell_price,pivot_put_sell_price = support_call_sell_price,support_put_sell_price
                pivot_call_file_name, pivot_put_file_name = support_call_file_name, support_put_file_name
                pivot_strike = support_strike
                call_pivot_profit,put_pivot_profit = call_support_profit,put_support_profit
                call_pivot_min_profit,call_pivot_max_profit = call_support_min_profit,call_support_max_profit
                put_pivot_min_profit,put_pivot_max_profit = put_support_min_profit,put_support_max_profit
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support-Pivot","Virtual_Change", "R1_Hit",
                                      pivot_strike,pivot_put_file_name,pivot_put_sell_price,
                                      pivot_strike,pivot_call_file_name,pivot_call_sell_price, call_pivot_profit,put_pivot_profit, call_pivot_min_profit, call_pivot_max_profit, put_pivot_min_profit, put_pivot_max_profit])


                support_strike = round(S3 / roundoff_factor) * roundoff_factor
                support_call_sell_price,support_put_sell_price,support_call_file_name, support_put_file_name = get_straddle_prices(zf1,folder_name_,instrument,support_strike,new_expiry_date,index_t, "SELL")
                support_call_position_active,support_put_position_active = both_position_status("Open")
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support","SELL", "S2_Hit",
                          support_strike,support_put_file_name,support_put_sell_price,
                          support_strike, support_call_file_name, support_call_sell_price, np.nan, np.nan, np.nan])
   

                call_support_min_profit,call_support_max_profit,put_support_min_profit,put_support_max_profit = initiate_min_max_profits()   
  
            # '''Close trade on expiry End_time'''
            elif((stop_date == expiry_date) & (index_t == end_time)):
                # if ((pivot_call_position_active == True) & (pivot_put_position_active == True)):
                future_price_end = df_weekly_futures_daily.loc[index_t]
                trade_end_date = stop_date
                
                pivot_call_position_active,pivot_put_position_active = both_position_status("Closed")
                support_call_position_active,support_put_position_active = both_position_status("Closed")
                resistance_call_position_active,resistance_put_position_active = both_position_status("Closed")
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Support","BUY", "Time_Exit",
                                      support_strike,support_put_file_name,support_put_buy_price,
                                      support_strike,support_call_file_name,support_call_buy_price, call_support_profit,put_support_profit, call_support_min_profit, call_support_max_profit, put_support_min_profit, put_support_max_profit])
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Resistance","BUY", "Time_Exit",
                                      resistance_strike,resistance_put_file_name,resistance_put_buy_price,
                                      resistance_strike,resistance_call_file_name,resistance_call_buy_price, call_resistance_profit,put_resistance_profit, call_resistance_min_profit, call_resistance_max_profit, put_resistance_min_profit, put_resistance_max_profit])
                
                transactions_book.append([stop_date, stop_date_name, index_t, current_fp_price, "Pivot","BUY", "Time_Exit",
                                      pivot_strike,pivot_put_file_name,pivot_put_buy_price,
                                      pivot_strike,pivot_call_file_name,pivot_call_buy_price,call_pivot_profit,put_pivot_profit, call_pivot_min_profit, call_pivot_max_profit, put_pivot_min_profit, put_pivot_max_profit])
                
                # transactionbook.append([trade_start_date, date_name,expiry_date, start_time_t, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, call_sell_price, np.nan,trade_end_date, stop_date_name, index_,np.nan,future_price_end, end_atm_IV,call_buy_price, np.nan,min_profit,max_profit,trade_type_call,trade_type_put])

                break

transactionbook_df = pd.DataFrame(transactions_book[1:], columns = transactions_book[0])
transactionbook_df_final = transactionbook_df[transactionbook_df["Signal_Type"]!="Virtual_Change"]
transactionbook_df.to_csv("../res/Weekly_3_Straddle_gap_diff.csv" ,index=False)
