# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 21:03:54 2022

@author: Jatin
"""

import pandas as pd

# df_call_option = pd.read_csv(r"E:\2021\DEC_2021\GFDLNFO_TICK_03122021\BANKNIFTY27JAN2236000CE.NFO.csv")
# df_put_option = pd.read_csv(r"E:\2021\DEC_2021\GFDLNFO_TICK_03122021\BANKNIFTY30DEC2132400PE.NFO.csv")
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
    for i in range(period-1, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
                                                         df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
                                                         df['final_lb'].iat[i - 1]

    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period-1, len(df)):
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

    # Remove basic and final bands from the columns
    # df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb','TR', atr], inplace=True, axis=1)

    df.fillna(0, inplace=True)
    return df

def make_candle_data(df_put_option ,df_call_option, candle_freq_min):
    df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
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
    bars = SuperTrend(bars)
    time_temp=time_temp.fillna(method="bfill")
    time_temp.index = pd.to_datetime(time_temp.index,errors='coerce').strftime("%H:%M:%S")
    bars = bars.join(time_temp)
    bars.to_csv("../res/"+df_call_option["Ticker"][0][:-4]+"_"+df_put_option["Ticker"][0][:-4]+"_STR_Calculation2.csv")
    return bars

def get_data(df_put_option, df_call_option):
    # df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    # df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
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
    time_temp=time_temp.fillna(method="bfill")
    time_temp = time_temp.fillna(0)
    return time_temp

candle_freq_min = "3min"
supertrend_period = 10
supertrend_multiplier=3

stoploss_percent = 0.16
stoploss_percent_combined = 0.01
instrument = "BANKNIFTY"
otm_value_wed_thu = 200
expiry_freq = 'W'
check_combined_stoploss = False
check_individual_stoploss = False

# instrument = "NIFTY"
if instrument == "BANKNIFTY":
    roundoff_factor = 100
    start_time = "09:45:00"
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
day_profit = {}


date_list = ["22-12-2021"]
# transactions_book = [["Date", 'Day',"Time","FuturesPrice","Ref_FuturePrice","vix",'Upper_Band2','Upper_Band1','Lower_Band1','Lower_Band2','Instrument_NameL', 'BuyPriceL','BuyQtyL','Instrument_NameS', 'SellPriceS', 'SellQtyS', 'SellPriceL','SellQtyL','BuyPriceS','BuyQtyS',"Profit","trade_type"]]
transactions_book = [['Date','Day','Time', 'Future', 'ATM Strike',
       'CallStrike to Sell','PutStrike to Sell', 'Call_Sell', 
       'Put_Sell', 'Sum_Sell','Call Buy', 'Call PNL','Put Buy', 'Put PNL', 
       'Close_Type_Call','Close_Type_Put']]
# ,"02-11-2021", "02-11-2021", "03-11-2021", "08-11-2021", "09-11-2021", "10-11-2021"]

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
    future_price = df_weekly_futures[wfut_cols[0]][df_weekly_futures["Time"] == start_time].values[0]
            
    working_strike = round(future_price / roundoff_factor) * roundoff_factor
    # working_strike = 34000
    call_strike = working_strike + otm_value_wed_thu
    put_strike = working_strike - otm_value_wed_thu
        
    '''Get expiry date and then get file for both and call option for their respective Strike price'''
    expiry_date = get_expiry_date(date)    
    expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
    put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
    call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
    
    df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
    bars_call_put_data = make_candle_data(df_put_option ,df_call_option, candle_freq_min)
    call_put_data = get_data(df_put_option, df_call_option)
    
    df_weekly_futures1 = df_weekly_futures[[wfut_cols[0], "Time"]].copy()
    df_weekly_futures1.set_index("Time", inplace = True)
    bars_call_put_data[wfut_cols[0]] = df_weekly_futures1[wfut_cols[0]]
    '''Sell options at start time'''
    sell_price_put = call_put_data["Put_BuyPrice"].loc[start_time]
    sell_price_call = call_put_data["Call_BuyPrice"].loc[start_time]
    combined_premium = sell_price_put + sell_price_call
    initial_investment = (working_strike)*0.2*2
    max_loss = int(180000*stoploss_percent_combined/25)
    # max_loss = 72
    
    position_active_call = True
    position_active_put = True
    buy_put_price = 0
    buy_call_price = 0
    buy_call_time = 0
    buy_put_time = 0
    sq_off_type_C = 'Start_Trade_C'
    sq_off_type_P = 'Start_Trade_P'
    transactions_book.append([date,date_name,start_time,future_price,working_strike,call_strike,put_strike,sell_price_call,sell_price_put,combined_premium,np.nan,np.nan,np.nan,np.nan,sq_off_type_C,sq_off_type_P])
    
    for index_ in tqdm(bars_call_put_data[(bars_call_put_data.index >= start_time) & (bars_call_put_data.index <= end_time)].index):

        if (((position_active_call == False) & (position_active_put == False) & (bars_call_put_data["STX"][index_] == 'down'))):
            future_price = df_weekly_futures[wfut_cols[0]][df_weekly_futures["Time"] == index_].values[0]
                    
            working_strike = round(future_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike + otm_value_wed_thu
            put_strike = working_strike - otm_value_wed_thu
                
            '''Get expiry date and then get file for both and call option for their respective Strike price'''
            expiry_date = get_expiry_date(date)    
            expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
            df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
            
            bars_call_put_data = make_candle_data(df_put_option ,df_call_option, candle_freq_min)
            call_put_data = get_data(df_put_option, df_call_option)
            
            df_weekly_futures1 = df_weekly_futures[[wfut_cols[0], "Time"]].copy()
            df_weekly_futures1.set_index("Time", inplace = True)
            bars_call_put_data[wfut_cols[0]] = df_weekly_futures1[wfut_cols[0]]
            idx_c = np.searchsorted(call_put_data.index, index_)
            idx_p = np.searchsorted(call_put_data.index, index_)
            
            sell_price_put = call_put_data["Put_BuyPrice"][min(idx_p+1, len(call_put_data)-1)]
            sell_price_call = call_put_data["Call_BuyPrice"][min(idx_c+1, len(call_put_data)-1)]
            
            combined_premium = sell_price_put + sell_price_call
            position_active_call = True
            position_active_put = True
            buy_put_price = 0
            buy_call_price = 0
            buy_call_time = 0
            buy_put_time = 0
            sq_off_type_C = 'SuperTrend_S_C'
            sq_off_type_P = 'SuperTrend_S_P'
            transactions_book.append([date,date_name,index_,future_price,working_strike,call_strike,put_strike,sell_price_call,sell_price_put,combined_premium,np.nan,np.nan,np.nan,np.nan,sq_off_type_C,sq_off_type_P])
            # print(call_file_name[:-8] ," Call Sold : ", sell_price_call, put_file_name[:-8], " Put Sold : ", sell_price_put, " at Time : ", index_)
        
        if((position_active_call == True) & (position_active_put == True) & (check_combined_stoploss == True)):
            curr_combined_prem = bars_call_put_data["Call_plus_Put"][index_]
            # curr_combined_prem = call_put_data["Call_plus_Put"][index_] - buy_call_price - buy_put_price
            if(curr_combined_prem - combined_premium >= max_loss):
                # if(position_active_call == True):
                idx_c = np.searchsorted(call_put_data.index, index_)
                
                idx_p = np.searchsorted(call_put_data.index, index_)
                
                buy_call_price = call_put_data["Call_SellPrice"][min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                # if(position_active_put == True):
                buy_put_price = call_put_data["Put_SellPrice"][min(idx_p+1, len(call_put_data)-1)]                
                position_active_put = False
                
                # max_loss =  max_loss + initial_investment*0.01 + (sell_price_call-buy_call_price)
                sq_off_type_C = 'CombinedSL_CP'
                sq_off_type_P = 'CombinedSL_CP'
                # print("Combined Stop loss hit for both options buying at : ",index_)
                break
            
        if(position_active_call == True):
            # print("Check Call Position")
            if(bars_call_put_data["STX"][index_] == 'up'):
                
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                # print("SuperTrend hit for call option buying at : ",call_put_data.index[min(idx_c+1, len(call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'SuperTrend_C'
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan])
                
                
            elif((check_individual_stoploss == True) & (call_put_data["Call_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_call)):
                
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                # buy_put_price = df_rel_put_option["C"][df_rel_put_option["C"]["Time"] == df_rel_call_option["Time"][i]]
                position_active_call = False
                max_loss =  max_loss + (sell_price_call-buy_call_price)
                # print("Stop loss hit for call bought call option buying at : ",call_put_data.index[min(idx_c+1, len(call_put_data)-1)], " for : ",buy_call_price , " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'Stoploss_C'
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan])
            
            elif((check_combined_stoploss == True) & ((sell_price_call - call_put_data["Call_SellPrice"][index_]) <= -1*max_loss) & (position_active_put == False)):
                
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan])
                sq_off_type_C = 'CombinedSL_C'
                # continue
            
            elif(index_ == end_time):
                
                idx_c = np.searchsorted(call_put_data.index, index_)
                buy_call_price = call_put_data["Call_SellPrice"].iloc[min(idx_c+1, len(call_put_data)-1)]
                position_active_call = False
                # print("Time Close hit for call option buying at : ",call_put_data.index[min(idx_c+1, len(call_put_data)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'EndTime_C'
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,buy_call_price,sell_price_call-buy_call_price,np.nan,np.nan,sq_off_type_C,np.nan])

                # continue
        
        if(position_active_put == True):
            if(bars_call_put_data["STX"][index_] == 'up'):
                
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                # print("SuperTrend hit for put option buying at : ",bars_call_put_data.index[min(idx_p+1, len(call_put_data)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price))
                sq_off_type_P = 'SuperTrend_P'
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P])

                
            elif((check_individual_stoploss == True) & (call_put_data["Put_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_put)):
                
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                max_loss =  max_loss + (sell_price_put-buy_put_price)
                # print("Stop loss hit for put bought put option buying at : ",call_put_data.index[min(idx_p+1, len(call_put_data)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price) )            
                sq_off_type_P = 'Stoploss_P'
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P])
                # continue
            
            elif((check_combined_stoploss == True) & ((sell_price_put - call_put_data["Put_SellPrice"][index_]) <= -1*max_loss) & (position_active_call == False)):
                
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P])
                sq_off_type_P = 'CombinedSL_P'
                # continue
            
            elif(index_ == end_time):
                
                idx_p = np.searchsorted(call_put_data.index, index_)
                buy_put_price = call_put_data["Put_SellPrice"].iloc[min(idx_p+1, len(call_put_data)-1)]
                position_active_put = False
                # print("Time close hit for put option buying at : ",call_put_data.index[min(idx_p+1, len(call_put_data)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price))
                sq_off_type_P = 'EndTime_P'
                transactions_book.append([date,date_name,index_,bars_call_put_data[wfut_cols[0]][index_],working_strike,call_strike,put_strike,np.nan,np.nan,np.nan,np.nan,np.nan,buy_put_price,sell_price_put-buy_put_price,np.nan,sq_off_type_P])


day_profit_df = pd.DataFrame(transactions_book[1:], columns = transactions_book[0])
day_profit_df.to_csv("../res/Output1.csv", index = False)
