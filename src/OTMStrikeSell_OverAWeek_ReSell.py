# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 17:38:14 2022

@author: Jatin
"""


import pandas as pd
import numpy as np
import datetime
import datetime as dt
import math
import zipfile
from tqdm import tqdm
from datetime import timedelta


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
    time_temp=time_temp.fillna(method="bfill")
    return time_temp

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
    
# add  stoploss
date_details = pd.read_csv("Backtest_Dates_Mondays1.csv", header = 0).dropna()
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
    start_time ="09:20:01"
    end_time ="15:20:00"
    last_trade_open_time ="14:45:00"
    contract_size = 25
    # prefix ="BN"
    # spot_file_name ="BANKNIFTY.csv"
elif instrument =="NIFTY":
    roundoff_factor = 50
    start_time ="09:20:00"
    end_time ="15:25:00"
    last_trade_open_time ="15:00:00"
    contract_size = 50
    
extra_fraction = 0.05
percent_based_offset = False
premium_based_offset = True
call_premium = 20
put_premium = 20
discount_premium = 15
buy_put_hedge = False
buy_call_hedge = False
stoploss_fraction = 0.3
individual_stoploss_fraction = 3
check_individual_stoploss = True
clear_both_legs = True
check_stoploss = False

transactionbook = [["Trade_Start_date", "Date_name","expiry_date", "start_time", "future_price", "Call_Ticker", "Put_Ticker",
                    "Start_ATM_IV", "call_sell_price", "put_sell_price", "stop_date", "stop_date_name", "call_end_time","put_end_time",
                    "future_price_end","End_ATM_IV", "call_buy_price", "put_buy_price","min_total_profit","max_total_profit","trade_type_call","trade_type_put"]]

# date_list = [
# '26-02-2021']
date_list = [
'01-07-2022',
'08-07-2022',
'15-07-2022',
'22-07-2022']
# dates not present = "05-02-2021","26-03-2021",'05-04-2021','09-04-2021','04-03-2022', '12-02-2021'
profit_tracker = pd.DataFrame(columns = date_list)
for date in date_list:
    # print(date)
    count = 0
    folder_name, folder_name_ = get_folder_name(date)
    # finding the month name
    month_name=pd.to_datetime(date, format ="%d-%m-%Y").strftime("%B")
    dir_1=changing_path + date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    date_name_call = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    date_name_put = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    #Now finding the file_name that needs to be opened
    to_zip=dir_1+folder_name[:-1]+str(".zip")
    try:
        zf = zipfile.ZipFile(to_zip)
    except:
        print("Data not present : ", date)
        pass
    
    '''Get data on Friday/Monday. Future Price and sell call/put accordingly'''

    df_weekly_futures = get_future_prices(date)
    df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
    
    future_price = df_weekly_futures_prices.loc[start_time]
    atm_strike = round(future_price / roundoff_factor) * roundoff_factor
    start_atm_IV = df_weekly_futures[str(atm_strike) + "_IV"].loc[start_time]
    trade_start_date_call = date
    trade_start_date_put = date
    expiry_date = get_expiry_date(date)
    expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    between_days = pd.date_range(pd.to_datetime(date, format ="%d-%m-%Y"),pd.to_datetime(expiry_date, format ="%d-%m-%Y"),freq='d')
    between_days = [b for b in between_days if b.strftime("%A") not in ["Saturday", "Sunday"]]
    between_days = [b.strftime("%d-%m-%Y") for b in between_days if b.strftime("%d-%m-%Y") not in holidays_list["Date"].tolist()]
    
    if percent_based_offset == True:
        call_strike = round(future_price*(1+extra_fraction) / roundoff_factor) * roundoff_factor
        put_strike = round(future_price*(1-extra_fraction) / roundoff_factor) * roundoff_factor
        put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
        call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")

        df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
        df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
    elif premium_based_offset == True:
        call_strike = atm_strike
        put_strike = atm_strike
        put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
        call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
        
        df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
        df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
        time_temp = get_data(df_put_option, df_call_option)
        # try:
        while time_temp["Call_BuyPrice"].loc[start_time] > call_premium:
            call_strike = call_strike + roundoff_factor
            try:
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
            except:
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike-roundoff_factor)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                break
            time_temp = get_data(df_put_option, df_call_option)
        # except:
        #     print("Data not present : ", date)
        #     pass
            
        
        # try:
        while time_temp["Put_BuyPrice"].loc[start_time] > put_premium:
            put_strike = put_strike - roundoff_factor
            try:
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
            except:
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike+roundoff_factor)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                break
            time_temp = get_data(df_put_option, df_call_option)
        # except:
        #         print("Data not present : ", date)
        #         pass
        
        # if buy_call_hedge == True:
        # hedge_call_strike = call_strike + roundoff_factor
        # hedge_call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(hedge_call_strike)+str("CE.NFO.csv")
        # df_hedge_call_option = pd.read_csv(zf.open(folder_name_+hedge_call_file_name))
            # time_temp = get_data(df_put_option, df_call_option)
        # if buy_put_hedge == True:
        # hedge_put_strike = put_strike - roundoff_factor
        # hedge_put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(hedge_put_strike)+str("PE.NFO.csv")
        # df_hedge_put_option = pd.read_csv(zf.open(folder_name_ + hedge_put_file_name))
        
        # time_temp_hedge = get_data(df_hedge_put_option, df_hedge_call_option)
    # time_temp = get_data(df_put_option, df_call_option)
        
    call_sell_price = time_temp["Call_BuyPrice"].loc[start_time]
    put_sell_price = time_temp["Put_BuyPrice"].loc[start_time]
    # if buy_put_hedge == True:
    #     hedge_put_buy_price = time_temp_hedge["Put_SellPrice"].loc[start_time]
    # else:
    #     hedge_put_buy_price = np.nan
    # if buy_call_hedge == True:
    #     hedge_call_buy_price = time_temp_hedge["Call_SellPrice"].loc[start_time]
    # else:
    #     hedge_call_buy_price = np.nan
        
        
    call_position_active = True
    put_position_active = True

    min_profit = 100000000
    max_profit = -100000000    
    '''Check Stoploss for in between dates'''
    print(between_days)
    profit_list = []
    start_time_t_call = start_time
    start_time_t_put = start_time
    for stop_date in between_days:
        if ((call_position_active == False) & (put_position_active == False)):
            break
        print(stop_date)
        folder_name, folder_name_ = get_folder_name(stop_date)
        month_name=pd.to_datetime(stop_date, format ="%d-%m-%Y").strftime("%B")
        dir_1=changing_path + stop_date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(stop_date[-4:]) + '/'
        stop_date_name = pd.to_datetime(stop_date, format ="%d-%m-%Y").strftime("%A")
        to_zip=dir_1+folder_name[:-1]+str(".zip")
        zf1 = zipfile.ZipFile(to_zip)
        # print()
        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
        df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
        time_temp = get_data(df_put_option, df_call_option)
        df_weekly_futures = get_future_prices(stop_date)
        
        # if buy_call_hedge == True:
        # df_hedge_call_option = pd.read_csv(zf1.open(folder_name_+hedge_call_file_name))
        # if buy_put_hedge == True:
        # df_hedge_put_option = pd.read_csv(zf1.open(folder_name_ + hedge_put_file_name))
        
        # time_temp_hedge = get_data(df_hedge_put_option, df_hedge_call_option)
        df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
        
        for index_,row in tqdm(time_temp[time_temp.index >= start_time].iterrows()):
            # print(index_)
            if (call_position_active == True):
                call_buy_price = time_temp["Call_SellPrice"].loc[index_]
                # if buy_call_hedge == True:
                #     hedge_call_sell_price = time_temp_hedge["Call_BuyPrice"].loc[index_]
                #     hedge_call_profit = (hedge_call_sell_price - hedge_call_buy_price)
                #     call_profit = (call_sell_price - call_buy_price) + hedge_call_profit
                # else:
                #     hedge_call_sell_price = np.nan
                #     hedge_call_profit = 0
                call_profit = (call_sell_price - call_buy_price)
                    
                
            if (put_position_active == True):
                put_buy_price = time_temp["Put_SellPrice"].loc[index_]
                # if buy_put_hedge == True:
                #     hedge_put_sell_price = time_temp_hedge["Put_BuyPrice"].loc[index_]
                #     hedge_put_profit = (hedge_put_sell_price - hedge_put_buy_price)
                #     put_profit = (put_sell_price - put_buy_price) + hedge_put_profit
                # else:
                #     hedge_put_sell_price = np.nan
                #     hedge_put_profit = 0
                put_profit = (put_sell_price - put_buy_price)
                
            profit = call_profit + put_profit
            
            profit_list.append(profit)
            min_profit = min(min_profit,profit)
            max_profit = max(max_profit,profit)
            '''Check Individual Stoploss'''
            if (check_individual_stoploss == True):
                if((call_profit < -1*(individual_stoploss_fraction)*(call_sell_price)) & (call_position_active == True)):
                    call_position_active = False
                    trade_type_call = "Stoploss_Call"
                    trade_type_put = "Stoploss_Call"
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    trade_end_date = stop_date
                    print("Call Individual StopLoss hit",stop_date,expiry_date, index_)
                    
                    
                    if clear_both_legs == False:
                        transactionbook.append([trade_start_date_call, date_name_call,expiry_date, start_time_t_call, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, call_sell_price, np.nan,trade_end_date, stop_date_name, index_,np.nan,future_price_end, end_atm_IV,call_buy_price, np.nan,min_profit,max_profit,trade_type_call,trade_type_put])
                    else:
                        put_position_active = False
                        transactionbook.append([trade_start_date_call, date_name_call,expiry_date, start_time_t_call, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, call_sell_price, put_sell_price,trade_end_date, stop_date_name, index_,index_,future_price_end, end_atm_IV,call_buy_price, put_buy_price,min_profit,max_profit,trade_type_call,trade_type_put])
                        trade_start_date_put = stop_date
                    if stop_date_name != 'Thursday':
                        trade_start_date_call = stop_date
                        date_name_call = pd.to_datetime(trade_start_date_call, format ="%d-%m-%Y").strftime("%A")
                        start_time_t_call = index_
                        future_price = df_weekly_futures_prices.loc[index_]
                        start_atm_IV = end_atm_IV
                        
                        if percent_based_offset == True:
                            call_strike = round(future_price*(1+extra_fraction) / roundoff_factor) * roundoff_factor
                            put_strike = round(future_price*(1-extra_fraction) / roundoff_factor) * roundoff_factor
                            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
    
                            df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                            df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                        
                        elif premium_based_offset == True:
                            call_strike = end_atm_strike
                            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                            df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                            if clear_both_legs == True:
                                put_strike = end_atm_strike
                                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                        
                            time_temp = get_data(df_put_option, df_call_option)
                            while time_temp["Call_BuyPrice"].loc[index_] > call_premium:
                                call_strike = call_strike + roundoff_factor
                                try:
                                    call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                                    df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                                    time_temp = get_data(df_put_option, df_call_option)
                                except:
                                    call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike-roundoff_factor)+str("CE.NFO.csv")
                                    df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                                    time_temp = get_data(df_put_option, df_call_option)
                                    break
                                
                            if clear_both_legs == True:
                                while time_temp["Put_BuyPrice"].loc[start_time] > put_premium:
                                    put_strike = put_strike - roundoff_factor
                                    try:
                                        put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                                        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                                        time_temp = get_data(df_put_option, df_call_option)
                                    except:
                                        put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike+roundoff_factor)+str("PE.NFO.csv")
                                        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                                        time_temp = get_data(df_put_option, df_call_option)
                                        break
                                    
                                    
                        call_sell_price = time_temp["Call_BuyPrice"].loc[index_]
                        call_position_active = True
                        if clear_both_legs == True:
                            put_sell_price = time_temp["Put_BuyPrice"].loc[index_]
                            put_position_active = True
    
                        min_profit = 100000000
                        max_profit = -100000000    
                    
                if((put_profit < -1*(individual_stoploss_fraction)*(put_sell_price)) & (put_position_active == True)):
                    put_position_active = False
                    
                    trade_type_put = "Stoploss_Put"
                    trade_type_call = "Stoploss_Put"
                    # final_put_buy = put_buy_price
                    # final_put_profit = put_profit
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    trade_end_date = stop_date
                    print("Put Individual StopLoss hit",stop_date,expiry_date, index_)
                    if clear_both_legs == False:
                        transactionbook.append([trade_start_date_put, date_name_put,expiry_date, start_time_t_put, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, np.nan, put_sell_price,trade_end_date, stop_date_name, np.nan,index_,future_price_end, end_atm_IV,np.nan, put_buy_price,min_profit,max_profit,trade_type_call,trade_type_put])
                    if clear_both_legs == True:
                        call_position_active = False
                        transactionbook.append([trade_start_date_put, date_name_put,expiry_date, start_time_t_put, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, call_sell_price, put_sell_price,trade_end_date, stop_date_name, index_,index_,future_price_end, end_atm_IV,call_buy_price, put_buy_price,min_profit,max_profit,trade_type_call,trade_type_put])
                        trade_start_date_call = stop_date
                    
                    if stop_date_name != 'Thursday':
                        trade_start_date_put = stop_date
                        date_name_put = pd.to_datetime(trade_start_date_put, format ="%d-%m-%Y").strftime("%A")
                        start_time_t_put = index_
                        future_price = df_weekly_futures_prices.loc[index_]
                        start_atm_IV = end_atm_IV
                        if percent_based_offset == True:
                            call_strike = round(future_price*(1+extra_fraction) / roundoff_factor) * roundoff_factor
                            put_strike = round(future_price*(1-extra_fraction) / roundoff_factor) * roundoff_factor
                            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
    
                            df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                            df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                        
                        elif premium_based_offset == True:
                            put_strike = end_atm_strike
                            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                            df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                            if clear_both_legs == True:
                                call_strike = end_atm_strike
                                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                                df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                        
                            time_temp = get_data(df_put_option, df_call_option)
                            
                            if clear_both_legs == True:
                                while time_temp["Call_BuyPrice"].loc[start_time] > call_premium:
                                    call_strike = call_strike + roundoff_factor
                                    try:
                                        call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                                        df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                                        time_temp = get_data(df_put_option, df_call_option)
                                    except:
                                        call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike-roundoff_factor)+str("CE.NFO.csv")
                                        df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                                        time_temp = get_data(df_put_option, df_call_option)
                                        break
                                    
                            while time_temp["Put_BuyPrice"].loc[index_] > put_premium:
                                put_strike = put_strike - roundoff_factor
                                try:
                                    put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                                    time_temp = get_data(df_put_option, df_call_option)
                                    
                                except:
                                    put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike+roundoff_factor)+str("PE.NFO.csv")
                                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                                    time_temp = get_data(df_put_option, df_call_option)
                                    break
                                
                        put_sell_price = time_temp["Put_BuyPrice"].loc[index_]
                        put_position_active = True
                        if clear_both_legs == True:
                            call_sell_price = time_temp["Call_BuyPrice"].loc[index_]
                            call_position_active = True
                        
                        
                        min_profit = 100000000
                        max_profit = -100000000  
            '''Check Combined Stoploss'''
            # if((profit < -1*(stoploss_fraction)*(call_sell_price+put_sell_price)) & (check_stoploss == True) & ((call_position_active == True) | (put_position_active == False))):
            #     call_position_active = False
            #     put_position_active = False
            #     trade_type = "Stoploss_Both"
            #     print("StopLoss hit",date, date_name,expiry_date, index_)
            #     transactionbook.append([date, date_name,expiry_date, start_time, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, call_sell_price, put_sell_price, stop_date, stop_date_name, index_,future_price_end, end_atm_IV,call_buy_price, put_buy_price,min_profit,max_profit,trade_type])
            #     break
            
            '''Close trade on expiry End_time'''
            if((stop_date == expiry_date) & (index_ == end_time) & ((call_position_active == True) | (put_position_active == True))):
                if 
                future_price_end = df_weekly_futures_prices.loc[index_]
                end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[end_time]
                trade_end_date = stop_date
                if call_position_active == True:
                    call_position_active = False
                    trade_type_call = "EndTime_Call"
                    trade_type_put = np.nan
                    transactionbook.append([trade_start_date_call, date_name_call,expiry_date, start_time_t_call, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, call_sell_price, np.nan,trade_end_date, stop_date_name, index_,np.nan,future_price_end, end_atm_IV,call_buy_price, np.nan,min_profit,max_profit,trade_type_call,trade_type_put])

                    
                if put_position_active == True:
                    put_position_active = False
                    trade_type_put = "EndTime_Put"
                    trade_type_call = np.nan
                    transactionbook.append([trade_start_date_put, date_name_put,expiry_date, start_time_t_put, future_price, call_file_name[:-10], put_file_name[:-10],start_atm_IV, np.nan, put_sell_price,trade_end_date, stop_date_name, np.nan,index_,future_price_end, end_atm_IV,np.nan, put_buy_price,min_profit,max_profit,trade_type_call,trade_type_put])

                print("EndTime")
                break

    '''Get data for thursday expiry to buy back the options'''
    
transactionbook_df = pd.DataFrame(transactionbook[1:], columns = transactionbook[0])
transactionbook_df["Call_Profit"] = transactionbook_df['call_sell_price'] - transactionbook_df['call_buy_price']
transactionbook_df["Put_Profit"] = transactionbook_df['put_sell_price'] - transactionbook_df['put_buy_price']
transactionbook_df.fillna(0,inplace =True)
# transactionbook_df["Call_Hedge_Profit"] = transactionbook_df['Hedge_Call_Sell_Price'] - transactionbook_df['Hedge_Call_Buy_Price']
# transactionbook_df["Put_Hedge_Profit"] = transactionbook_df['Hedge_Put_Sell_Price'] - transactionbook_df['Hedge_Put_Buy_Price']

transactionbook_df["Total_Profit"] = transactionbook_df["Call_Profit"] + transactionbook_df["Put_Profit"]
transactionbook_df.to_csv("../res/OTMStrikeSell_"+str(call_premium)+"_Premium_Resell_New_TwoLeg1_"+str(individual_stoploss_fraction)+".csv", index = False) 


