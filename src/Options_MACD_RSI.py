#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 20:46:04 2023

@author: bnsl.j3
"""

import pandas as pd
import numpy as np
import datetime
# import matplotlib.pyplot as plt
from datetime import timedelta
# from dateutil.relativedelta import relativedelta, TH, WE
import datetime as dt
import zipfile
import warnings
from tqdm import tqdm

warnings.filterwarnings('ignore')

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

def get_future_prices(expiry_date,month_name):
    month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+expiry_date[-2:] +"/"+ pd.to_datetime(expiry_date , format = '%d-%m-%Y').strftime("%d%m%Y") +"_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    # df_weekly_futures.set_index("Time", inplace = True)
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
    # bars["Call_BuyPrice"] = call_put_data["Call_BuyPrice"]
    # bars["Put_BuyPrice"] = call_put_data["Put_BuyPrice"]
    # bars["Call_SellPrice"] = call_put_data["Call_SellPrice"]
    # bars["Put_SellPrice"] = call_put_data["Put_SellPrice"]
    # bars["Call_LTP"] = df_call_option["LTP"]
    # bars["Put_LTP"] = df_put_option["LTP"]
    # bars["Combined_LTP"] = time_temp["Put_LTP"] + time_temp["Call_LTP"]
    # bars = EMA(bars, "close", str(period) + "_EMA", period)
    # bars.to_csv("../res/"+df_call_option["Ticker"][0][:-4]+"_"+df_put_option["Ticker"][0][:-4]+"_STR_Calculation2.csv")
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

# add  stoploss
date_details = pd.read_csv("All_Dates.csv", header = 0).dropna(axis = 1)
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
    end_time ="15:21:00"
    last_trade_open_time ="14:45:00"
    contract_size = 25
    # prefix ="BN"
    # spot_file_name ="BANKNIFTY.csv"
elif instrument =="NIFTY":
    roundoff_factor = 50
    start_time ="09:27:00"
    end_time ="15:21:00"
    last_trade_open_time ="15:00:00"
    contract_size = 50

transaction_cost_percent_sell = 0.1125
transaction_cost_percent_buy = 0.05
candle_freq_min = "15min"
ema_period = 50
rsi_period = 5
rsi_upper_threshold = 75
rsi_below_threshold = 25
stop_loss = 25
profit_booking = 50
transactions_book = [['Date', 'Day', 'Entry_Time', 'Entry_Future', "Exit_Time", 'Exit_Future', 'ATM Strike',
                    'CallStrike', 'PutStrike', 'Put_Sell_Name', 'Call_Sell_Name', 'Sell Price', 'Buy Price',
                    'Trade_Type_Entry', 'Trade_Type_Exit', "Signal_Type", "Min_Profit", "Max_Profit"]]


def get_macd(price, slow, fast, smooth):
    # price, slow, fast, smooth = bars_future_data["close"], 26, 12, 9
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join = 'inner', axis = 1)
    return df

for date in tqdm(date_list[1:]):
    # date = '27-07-2022'
    # print(date)
    folder_name, folder_name_ = get_folder_name(date)
    month_name=pd.to_datetime(date, format = "%d-%m-%Y").strftime("%B")
    date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    dir_1=changing_path + date[-4:] + "/" + month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    to_zip=dir_1+folder_name[:-1]+str(".zip")
    
    zf = zipfile.ZipFile(to_zip)
                
    '''read Futures file for that day. took future's price as of start_time to calculate ATM'''
    current_Date_index = date_list.index(date)
    df_weekly_futures = get_future_prices(date,month_name)
    df_weekly_futures["New_Index"] = date + " " +df_weekly_futures["Time"]
    df_weekly_futures["New_Index"] = pd.to_datetime(df_weekly_futures["New_Index"], format="%d-%m-%Y %H:%M:%S")
    df_weekly_futures.set_index("New_Index", inplace = True)
    df_weekly_futures=df_weekly_futures.fillna(method="ffill")
    
    wfut_cols = [x for x in df_weekly_futures.columns if"WFUT"in x]
    df_weekly_futures.rename(columns = {wfut_cols[0]:"ToAdd"}, inplace = True)
    
    previous_date = date_list[current_Date_index - 1]
    previous_day_future = get_future_prices(previous_date,pd.to_datetime(previous_date, format = "%d-%m-%Y").strftime("%B"))
    previous_day_future["New_Index"] = previous_date + " " +previous_day_future["Time"]
    previous_day_future["New_Index"] = pd.to_datetime(previous_day_future["New_Index"], format="%d-%m-%Y %H:%M:%S")
    previous_day_future.set_index("New_Index", inplace = True)
    previous_day_future=previous_day_future.fillna(method="ffill")
    
    wfut_cols_pre = [x for x in previous_day_future.columns if"WFUT"in x]
    previous_day_future.rename(columns = {wfut_cols_pre[0]:"ToAdd"}, inplace = True)
    # combined_fut_prices = pd.concat([previous_day_future[['FUT_B', 'FUT_S']],df_weekly_futures[['FUT_B', 'FUT_S']]])
    combined_fut_prices = pd.concat([previous_day_future[["ToAdd"]],df_weekly_futures[["ToAdd"]]])
    combined_fut_prices["Avg_Fut_Price"] = combined_fut_prices["ToAdd"]
    # combined_fut_prices = combined_fut_prices.drop(['FUT_S', 'FUT_B'], axis  =1)
    
    
    bars_future_data = make_candle_data_index(combined_fut_prices,candle_freq_min)
    bars_future_data = get_macd(bars_future_data, 26, 12, 9)
    # EMA(bars_future_data, "close", str(ema_period) + "_EMA", ema_period)
    bars_future_data[str(rsi_period) + "_RSI"] = RSI(bars_future_data,rsi_period)
    bars_future_data = bars_future_data.reset_index()
    bars_future_data['New_Index']=bars_future_data['New_Index'].astype(str)
    
    bars_future_data[['Date', 'Time']] = bars_future_data.New_Index.str.split(" ", expand = True)
    """Check here date time format"""
    bars_future_data = bars_future_data[bars_future_data["Date"] == pd.to_datetime(date, format = "%d-%m-%Y").strftime("%Y-%m-%d")]
    bars_future_data.set_index("Time", inplace = True)
    bars_future_data = bars_future_data.drop(['New_Index', 'Date'], axis =1)
    df_weekly_futures.set_index("Time", inplace = True)
    # df_weekly_futures1 =df_weekly_futures[['FUT_B', 'FUT_S']]
    # df_weekly_futures1["Avg_Fut_Price"] = (df_weekly_futures['FUT_B'] + df_weekly_futures['FUT_S'])/2
    # bars_future_data[wfut_cols[0]] = df_weekly_futures[wfut_cols[0]]
    
    call_position_active = False
    put_position_active = False
    trade_type = ""
    signal_type = ""
    put_sell_price = 0
    put_buy_price = 0
    call_sell_price = 0
    call_buy_price = 0
    # sq_off_type_C = 'Start_Trade_C'
    # sq_off_type_P = 'Start_Trade_P'
    time_temp=pd.read_csv("TimeTemplate.csv", index_col=("Time"))
    full_time_data = pd.concat([time_temp, bars_future_data], axis = 1)
    
    # for index_ in tqdm(full_time_data[(full_time_data.index >= start_time) & (full_time_data.index <= end_time)].index):
    for index_ in (bars_future_data[(bars_future_data.index >= start_time) & (bars_future_data.index <= end_time)].index):
        # if index_ == '09:36:00':
        #     print("break")
        #     break
        # current_future_price = df_weekly_futures["ToAdd"].loc[index_]
        # current_future_price = df_weekly_futures1["Avg_Fut_Price"].loc[index_]
        # bars_call_put_data = make_candle_data(df_put_option ,df_call_option, "3min")
        # call_put_data = get_data(df_put_option, df_call_option)
        minus_1_index = (pd.to_datetime(index_) - timedelta(hours=0, minutes=int(candle_freq_min[:-3]))).strftime("%H:%M:%S")
        minus_2_index = (pd.to_datetime(index_) - timedelta(hours=0, minutes=2*int(candle_freq_min[:-3]))).strftime("%H:%M:%S")
        minus_3_index = (pd.to_datetime(index_) - timedelta(hours=0, minutes=3*int(candle_freq_min[:-3]))).strftime("%H:%M:%S")
        
        # Description: EMA RSI Strategy with 50 PB and 25 SL on Option Prices; 50 EMA; 3min Candle; RSI Long 75 and  RSI Short 25; RSI (Period=7);
        # Candle(-1)>EMA(-1);
        # RSI(-1)>75 and RSI(0)>RSI(-1);
        # Open(-2)<Close(-2)<Close(-1)<Close(0);
        # Close(-1)>High(-2) + Close(0)>High(-1)
        """ENTRY CONDITIONS"""
        long_entry_condition_2 = (bars_future_data['close'][minus_2_index] > bars_future_data[str(ema_period)+'_EMA'][minus_2_index])
        long_entry_condition_3 = (bars_future_data[str(rsi_period)+ "_RSI"][minus_2_index] > rsi_upper_threshold)
        long_entry_condition_5 = (bars_future_data[str(rsi_period)+ "_RSI"][minus_1_index] > (bars_future_data[str(rsi_period)+ "_RSI"][minus_2_index]))
        
        long_entry_condition_1 = (bars_future_data["close"][minus_3_index] > bars_future_data["open"][minus_3_index])
        long_entry_condition_4 = (bars_future_data["close"][minus_2_index] > bars_future_data["high"][minus_3_index])
        long_entry_condition_6 = (bars_future_data["close"][minus_1_index] > bars_future_data["high"][minus_2_index])
        
        short_entry_condition_2 = (bars_future_data['close'][minus_2_index] < bars_future_data[str(ema_period)+'_EMA'][minus_2_index])
        short_entry_condition_3 = (bars_future_data[str(rsi_period)+ "_RSI"][minus_2_index] <rsi_below_threshold)
        short_entry_condition_5 = (bars_future_data[str(rsi_period)+ "_RSI"][minus_1_index] < (bars_future_data[str(rsi_period)+ "_RSI"][minus_2_index]))
        
        short_entry_condition_1 = (bars_future_data["close"][minus_3_index] < bars_future_data["open"][minus_3_index])
        short_entry_condition_4 = (bars_future_data["close"][minus_2_index] < bars_future_data["low"][minus_3_index])
        short_entry_condition_6 = (bars_future_data["close"][minus_1_index] < bars_future_data["low"][minus_2_index])
        
        current_time_index = bars_future_data.index.get_loc(minus_1_index)
        # bars_future_data[bars_future_data.index == index_].index[0]
        next_time = bars_future_data.index[current_time_index + 1]
        
        full_data_start_row = full_time_data.index.get_loc(minus_1_index)
        full_data_end_row = full_time_data.index.get_loc(next_time)
        
        # current_future_price = bars_future_data["open"].loc[index_]        
        
        if(long_entry_condition_1 & long_entry_condition_2 & long_entry_condition_3 & (not put_position_active) & (not call_position_active) & long_entry_condition_4 & long_entry_condition_5 & long_entry_condition_6):
            current_future_price = df_weekly_futures["ToAdd"].loc[minus_1_index]
            working_strike = round(current_future_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike 
            put_strike = working_strike
                
            '''Get expiry date and then get file for both and call option for their respective Strike price'''
            expiry_date = get_expiry_date(date)    
            expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
            df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
            call_put_data = get_data(df_put_option, df_call_option)
            
            # full_time_data = pd.concat([full_time_data, call_put_data], axis = 1)
            full_time_data['Call_BuyPrice'] = call_put_data['Call_BuyPrice']
            full_time_data['Put_BuyPrice'] = call_put_data['Put_BuyPrice']
            full_time_data['Call_SellPrice'] = call_put_data['Call_SellPrice']
            full_time_data['Put_SellPrice'] =call_put_data['Put_SellPrice']
            
            put_position_active = True
            put_sell_price = call_put_data["Put_BuyPrice"][minus_1_index]
            trade_type_entry = "Entry_Trade_P"
            signal_type = "BUY"
            entry_time = minus_1_index
            min_profit = 100000000
            max_profit = -100000000
            entry_future_price = current_future_price
        
        if(short_entry_condition_1 & short_entry_condition_2 & short_entry_condition_3 & (not call_position_active) & (not put_position_active) & short_entry_condition_4 & short_entry_condition_5 & short_entry_condition_6):
            current_future_price = df_weekly_futures["ToAdd"].loc[minus_1_index]
            working_strike = round(current_future_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike 
            put_strike = working_strike
                
            '''Get expiry date and then get file for both and call option for their respective Strike price'''
            expiry_date = get_expiry_date(date)    
            expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
            df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
            call_put_data = get_data(df_put_option, df_call_option)
            
            # full_time_data = pd.concat([full_time_data, call_put_data], axis = 1)
            full_time_data['Call_BuyPrice'] = call_put_data['Call_BuyPrice']
            full_time_data['Put_BuyPrice'] = call_put_data['Put_BuyPrice']
            full_time_data['Call_SellPrice'] = call_put_data['Call_SellPrice']
            full_time_data['Put_SellPrice'] =call_put_data['Put_SellPrice']
            
            call_position_active = True
            call_sell_price = call_put_data["Call_BuyPrice"][minus_1_index]
            trade_type_entry = "Entry_Trade_C"
            entry_time = minus_1_index
            signal_type = "SELL"
            entry_future_price = current_future_price
            min_profit = 100000000
            max_profit = -100000000
        # 
        if (short_entry_condition_1 & short_entry_condition_2 & short_entry_condition_3 & (put_position_active) & short_entry_condition_4 & short_entry_condition_5 & short_entry_condition_6):
            current_future_price = df_weekly_futures["ToAdd"].loc[minus_1_index]
            trade_type_exit = "Exit_Sell_Signal_P"
            profit = put_sell_price - call_put_data["Put_SellPrice"][minus_1_index]               
            min_profit = min(min_profit,profit)
            max_profit = max(max_profit,profit)
            put_position_active = False
            put_buy_price = full_time_data["Put_SellPrice"][minus_1_index]
            transactions_book.append([date,date_name,entry_time, entry_future_price,minus_1_index,current_future_price, working_strike,
                    call_strike,put_strike, put_file_name[:-8],""
                    ,put_sell_price, put_buy_price, 
                    trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
        
        if(long_entry_condition_1 & long_entry_condition_2 & long_entry_condition_3 & (call_position_active) & long_entry_condition_4 & long_entry_condition_5 & long_entry_condition_6):
            current_future_price = df_weekly_futures["ToAdd"].loc[minus_1_index]
            trade_type_exit = "Exit_Sell_Signal_C"
            profit = call_sell_price - call_put_data["Call_SellPrice"][minus_1_index]               
            min_profit = min(min_profit,profit)
            max_profit = max(max_profit,profit)
            call_position_active = False
            call_buy_price = full_time_data["Call_SellPrice"][minus_1_index]
            transactions_book.append([date,date_name,entry_time, entry_future_price,minus_1_index,current_future_price, working_strike,
                    call_strike,put_strike,"", call_file_name[:-8],call_sell_price, call_buy_price, 
                    trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
            
            
        if put_position_active:
            # """Time Exit"""
            for row_number in range(full_data_start_row, full_data_end_row, 1):
                _index_ = full_time_data.index[row_number]
                current_future_price = df_weekly_futures["ToAdd"].loc[_index_]
                profit = put_sell_price - call_put_data["Put_SellPrice"][_index_]               
                min_profit = min(min_profit,profit)
                max_profit = max(max_profit,profit)
                # print(_index_)
                if(end_time == _index_):
                    trade_type_exit = "Exit_Trade_Time_P"
                    put_position_active = False
                    put_buy_price = full_time_data["Put_SellPrice"][_index_]
                    transactions_book.append([date,date_name,entry_time, entry_future_price,_index_,current_future_price, working_strike,
                           call_strike,put_strike, put_file_name[:-8],"",put_sell_price, put_buy_price, 
                           trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
                    break
                # """Profit Exit"""
                elif(profit > profit_booking):
                # elif((current_future_price - entry_future_price > 100)):
                    put_position_active = False
                    trade_type_exit = "Exit_Trade_Profit_P"
                    put_buy_price = full_time_data["Put_SellPrice"][_index_]
                    transactions_book.append([date,date_name,entry_time, entry_future_price,_index_,current_future_price, working_strike,
                           call_strike,put_strike, put_file_name[:-8],""
                           ,put_sell_price, put_buy_price, 
                           trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
                    break
                # '''StopLoss Exit'''
                elif(profit < -1*stop_loss):
                # elif((current_future_price - entry_future_price < -200)):
                    trade_type_exit = "Exit_Trade_Stoploss_P"
                    put_position_active = False
                    put_buy_price = full_time_data["Put_SellPrice"][_index_]
                    transactions_book.append([date,date_name,entry_time, entry_future_price,_index_,current_future_price, working_strike,
                           call_strike,put_strike, put_file_name[:-8],""
                           ,put_sell_price, put_buy_price, 
                           trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
                    break
                
                
        if call_position_active:
            for row_number in range(full_data_start_row, full_data_end_row, 1):
                _index_ = full_time_data.index[row_number]
                current_future_price = df_weekly_futures["ToAdd"].loc[_index_]
                profit = call_sell_price - call_put_data["Call_SellPrice"][_index_]               
                min_profit = min(min_profit,profit)
                max_profit = max(max_profit,profit)
                
                if(end_time == _index_):
                    trade_type_exit = "Exit_Trade_Time_C"
                    call_position_active = False
                    call_buy_price = full_time_data["Call_SellPrice"][_index_]
                    transactions_book.append([date,date_name,entry_time, entry_future_price,_index_,current_future_price, working_strike,
                           call_strike,put_strike,"", call_file_name[:-8]
                           ,call_sell_price, call_buy_price, 
                           trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
                    break
                    
                elif(profit < -1*stop_loss):
                # elif((current_future_price - entry_future_price > 200)):
                    call_position_active = False
                    trade_type_exit = "Exit_Trade_Stoploss_C"
                    call_buy_price = full_time_data["Call_SellPrice"][_index_]
                    transactions_book.append([date,date_name,entry_time, entry_future_price,_index_,current_future_price, working_strike,
                           call_strike,put_strike,"", call_file_name[:-8]
                           ,call_sell_price, call_buy_price, 
                           trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
                    break
                    
                elif(profit > profit_booking):
                # elif((current_future_price - entry_future_price < -100)):
                    trade_type_exit = "Exit_Trade_Profit_C"
                    call_position_active = False
                    call_buy_price = full_time_data["Call_SellPrice"][_index_]
                    transactions_book.append([date,date_name,entry_time, entry_future_price,_index_,current_future_price, working_strike,
                           call_strike,put_strike,"", call_file_name[:-8]
                           ,call_sell_price, call_buy_price, 
                           trade_type_entry,trade_type_exit,signal_type, min_profit, max_profit])
                    break
            
# name = 
transactionbook_df = pd.DataFrame(transactions_book[1:], columns = transactions_book[0])
transactionbook_df["Gross_Profit"] = transactionbook_df["Sell Price"] - transactionbook_df["Buy Price"]
transactionbook_df["Transaction_Cost"] = ((transactionbook_df["Sell Price"]*transaction_cost_percent_sell + transactionbook_df["Buy Price"])*transaction_cost_percent_buy)/100
transactionbook_df["Net_Profit"] = transactionbook_df["Gross_Profit"] - transactionbook_df["Transaction_Cost"]

transactionbook_df.to_csv("../res/Options_EMA_RSI_"+str(rsi_period)+"_"+candle_freq_min+".csv", index = False)
            