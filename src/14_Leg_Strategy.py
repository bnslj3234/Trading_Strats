#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 19:37:47 2023

@author: bnsl.j3
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

path_for_weekly_futures=r'/Users/bnsl.j3/Desktop/Jatin Bansal/Options/BankNifty Output/'
changing_path = "/Users/bnsl.j3/Desktop/Jatin Bansal/Options/"
date_details = pd.read_csv("Backtest_Dates_S.csv", header = 0).dropna()
date_list = date_details["Date"].tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] == "Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] == "Wednesday"].tolist()
# wed_thu_hol = holidays_list[(holidays_list["Day"] == "Thursday") | (holidays_list["Day"] == "Wednesday")]["Date"].tolist()
# path_for_weekly_futures=r'D:/Options/BankNifty Output'

instrument ="BANKNIFTY"

# instrument ="NIFTY"
if instrument =="BANKNIFTY":
    roundoff_factor = 100
    # start_time ="09:25:01"
    # end_time ="15:00:00"
    last_trade_open_time ="14:45:00"
    contract_size = 25
    # prefix ="BN"
    # spot_file_name ="BANKNIFTY.csv"
elif instrument =="NIFTY":
    roundoff_factor = 50
    # start_time ="09:20:00"
    # end_time ="15:25:00"
    last_trade_open_time ="15:00:00"
    contract_size = 50
    
strategy_dict = { "STR1"  : {"RUN_STR" : True,'start_time'  : "09:19:00",'end_time' :"09:43:00", 'stop_loss_points' : True, 'SL_points' : 20, 'stop_loss_percent' : False, 'SL_percent' : 0.20, 'stop_loss_fraction' : False, 'SL_fraction' : 0.6, "TSL" : False},
                  "STR10" : {"RUN_STR" : True,'start_time'  : "14:59:00",'end_time' :"15:26:00", 'stop_loss_points' : True, 'SL_points' : 20, 'stop_loss_percent' : False, 'SL_percent' : 0.20, 'stop_loss_fraction' : False, 'SL_fraction' : 0.6, "TSL" : False},
                  "STR11" : {"RUN_STR" : True,'start_time'  : "15:01:00",'end_time' :"15:26:00", 'stop_loss_points' : True, 'SL_points' : 20, 'stop_loss_percent' : False, 'SL_percent' : 0.20, 'stop_loss_fraction' : False, 'SL_fraction' : 0.6, "TSL" : False},
                  "STR13" : {"RUN_STR" : True,'start_time'  : "15:03:00",'end_time' :"15:26:00", 'stop_loss_points' : True, 'SL_points' : 20, 'stop_loss_percent' : False, 'SL_percent' : 0.20, 'stop_loss_fraction' : False, 'SL_fraction' : 0.6, "TSL" : False},
                  "STR14" : {"RUN_STR" : True,'start_time'  : "15:07:00",'end_time' :"15:26:00", 'stop_loss_points' : True, 'SL_points' : 20, 'stop_loss_percent' : False, 'SL_percent' : 0.20, 'stop_loss_fraction' : False, 'SL_fraction' : 0.6, "TSL" : False},
                  "STR2"  : {"RUN_STR" : True,'start_time'  : "09:19:00",'end_time' :"11:03:00", 'stop_loss_points' : True, 'SL_points' : 20, 'stop_loss_percent' : True, 'SL_percent' : 0.20, 'stop_loss_fraction' : False, 'SL_fraction' : 0.6, "TSL" : True},

                }


for strrat_1 in ["STR1","STR10","STR11","STR13","STR14"]:
    
    transactionbook1 = [["Trade_Start_date", "Date_name","expiry_date", "start_time", "future_price", "Call_Ticker", "Put_Ticker", "call_sell_price", "put_sell_price","end_time",
                        "future_price_end","End_ATM_IV", "call_buy_price", "put_buy_price","min_profit","max_profit","trade_type",]]

    for date in date_list:
        print(date)
        folder_name, folder_name_ = get_folder_name(date)
        # finding the month name
        month_name=pd.to_datetime(date, format ="%d-%m-%Y").strftime("%B")
        dir_1=changing_path + date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
        date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
        #Now finding the file_name that needs to be opened
        to_zip=dir_1+folder_name[:-1]+str(".zip")
        try:
            zf = zipfile.ZipFile(to_zip)
        except:
            print("Data not present : ", date)
            pass
            
        df_weekly_futures = get_future_prices(date)
        df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
        expiry_date = get_expiry_date(date)
        expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    
        if strategy_dict[strrat_1]["RUN_STR"] == True:
            
            future_price1 = df_weekly_futures_prices.loc[strategy_dict[strrat_1]["start_time"]]
            atm_strike1 = round(future_price1 / roundoff_factor) * roundoff_factor
            
            if atm_strike1 == 0:
                continue
            
            call_strike = atm_strike1
            put_strike = atm_strike1
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option1 = pd.read_csv(zf.open(folder_name_ + put_file_name))
            df_call_option1 = pd.read_csv(zf.open(folder_name_+call_file_name))
        
            time_temp1 = get_data(df_put_option1, df_call_option1)
            call_sell_price1 = time_temp1["Call_BuyPrice"].loc[strategy_dict[strrat_1]["start_time"]]
            put_sell_price1 = time_temp1["Put_BuyPrice"].loc[strategy_dict[strrat_1]["start_time"]]
            start_atm_IV = df_weekly_futures[str(atm_strike1) + "_IV"].loc[strategy_dict[strrat_1]["start_time"]]
            call_position_active1 = True
            put_position_active1 = True
            min_profit1 = 100000000
            max_profit1 = -100000000  
            for index_,row in tqdm(time_temp1[(time_temp1.index >= strategy_dict[strrat_1]["start_time"]) & (time_temp1.index <= strategy_dict[strrat_1]["end_time"]) ].iterrows()):
                # print(index_)
                if call_position_active1 == True:
                    call_buy_price1 = time_temp1["Call_SellPrice"].loc[index_]
                    call_profit1 = (call_sell_price1 - call_buy_price1)
                 
                if put_position_active1 == True:
                    put_buy_price1 = time_temp1["Put_SellPrice"].loc[index_]
                    put_profit1 = (put_sell_price1 - put_buy_price1)
                    
                profit1 = call_profit1 + put_profit1
                # profit_list.append(profit)
                min_profit1 = min(min_profit1,profit1)
                max_profit1 = max(max_profit1,profit1)
                
                if((call_profit1 < -1*strategy_dict[strrat_1]["SL_points"]) & (call_position_active1 == True) & (strategy_dict[strrat_1]["stop_loss_points"] == True)):
                    call_position_active1 = False
                    trade_type1 = "Stoploss_Call"
                    final_call_buy1 = call_buy_price1
                    final_call_profit1 = call_profit1
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], call_sell_price1, 0, index_,future_price_end, end_atm_IV,call_buy_price1, 0,min_profit1,max_profit1,trade_type1])
    
                if((put_profit1 < -1*strategy_dict[strrat_1]["SL_points"]) & (put_position_active1 == True) & (strategy_dict[strrat_1]["stop_loss_points"] == True)):
                    put_position_active1 = False
                    trade_type1 = "Stoploss_put"
                    final_put_buy1 = put_buy_price1
                    final_put_profit1 = put_profit1
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], 0, put_sell_price1, index_,future_price_end, end_atm_IV,0, put_buy_price1,min_profit1,max_profit1,trade_type1])
                
                if((index_ == strategy_dict[strrat_1]["end_time"]) & ((call_position_active1 == True) | (put_position_active1 == True))):
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    
                    if(call_position_active1 == True):
                        call_position_active1 = False
                        trade_type1 = "EndTime_Call"
                        final_call_buy1 = call_buy_price1
                        final_call_profit1 = call_profit1
                        transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], call_sell_price1, 0, index_,future_price_end, end_atm_IV,call_buy_price1, 0,min_profit1,max_profit1,trade_type1])
    
                    if(put_position_active1 == True):
                        put_position_active1 = False
                        trade_type1 = "EndTime_put"
                        final_put_buy1 = put_buy_price1
                        final_put_profit1 = put_profit1
                        transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], 0, put_sell_price1, index_,future_price_end, end_atm_IV,0, put_buy_price1,min_profit1,max_profit1,trade_type1])
    
                    break
        
    transactionbook_df1 = pd.DataFrame(transactionbook1[1:], columns = transactionbook1[0])
    transactionbook_df1["Call_Profit"] = transactionbook_df1['call_sell_price'] - transactionbook_df1['call_buy_price']
    transactionbook_df1["Put_Profit"] = transactionbook_df1['put_sell_price'] - transactionbook_df1['put_buy_price']
    transactionbook_df1["Total_Profit"] = transactionbook_df1["Call_Profit"] + transactionbook_df1["Put_Profit"]
    transactionbook_df1.to_csv(r"/Users/bnsl.j3/Desktop/Jatin Bansal/Options/OptionsCode/res/14Leg_Output_"+strrat_1+'.csv')
    
for strrat_1 in ["STR2"]:
    
    transactionbook1 = [["Trade_Start_date", "Date_name","expiry_date", "start_time", "future_price", "Call_Ticker", "Put_Ticker", "call_sell_price", "put_sell_price","end_time",
                        "future_price_end","End_ATM_IV", "call_buy_price", "put_buy_price","min_profit","max_profit","trade_type",]]

    for date in date_list:
        print(date)
        folder_name, folder_name_ = get_folder_name(date)
        # finding the month name
        month_name=pd.to_datetime(date, format ="%d-%m-%Y").strftime("%B")
        dir_1=changing_path + date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
        date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
        #Now finding the file_name that needs to be opened
        to_zip=dir_1+folder_name[:-1]+str(".zip")
        try:
            zf = zipfile.ZipFile(to_zip)
        except:
            print("Data not present : ", date)
            pass
            
        df_weekly_futures = get_future_prices(date)
        df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
        expiry_date = get_expiry_date(date)
        expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    
        if strategy_dict[strrat_1]["RUN_STR"] == True:
            call_premium = 100
            put_premium = 100
            
            future_price1 = df_weekly_futures_prices.loc[strategy_dict[strrat_1]["start_time"]]
            atm_strike1 = round(future_price1 / roundoff_factor) * roundoff_factor
            
            if atm_strike1 == 0:
                continue
            
            call_strike = atm_strike1
            put_strike = atm_strike1
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
            df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
        
            time_temp = get_data(df_put_option, df_call_option)
            while time_temp["Call_BuyPrice"].loc[strategy_dict[strrat_1]["start_time"]] > call_premium:
                call_strike = call_strike + roundoff_factor
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
                time_temp = get_data(df_put_option, df_call_option)
            
            
            while time_temp["Put_BuyPrice"].loc[strategy_dict[strrat_1]["start_time"]] > put_premium:
                put_strike = put_strike - roundoff_factor
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
                time_temp = get_data(df_put_option, df_call_option)
                
            
            call_sell_price1 = time_temp1["Call_BuyPrice"].loc[strategy_dict[strrat_1]["start_time"]]
            put_sell_price1 = time_temp1["Put_BuyPrice"].loc[strategy_dict[strrat_1]["start_time"]]
            start_atm_IV = df_weekly_futures[str(atm_strike1) + "_IV"].loc[strategy_dict[strrat_1]["start_time"]]
            call_position_active1 = True
            put_position_active1 = True
            min_profit1 = 100000000
            max_profit1 = -100000000
            for index_,row in tqdm(time_temp1[(time_temp1.index >= strategy_dict[strrat_1]["start_time"]) & (time_temp1.index <= strategy_dict[strrat_1]["end_time"]) ].iterrows()):
                # print(index_)
                if call_position_active1 == True:
                    call_buy_price1 = time_temp1["Call_SellPrice"].loc[index_]
                    call_profit1 = (call_sell_price1 - call_buy_price1)
                 
                if put_position_active1 == True:
                    put_buy_price1 = time_temp1["Put_SellPrice"].loc[index_]
                    put_profit1 = (put_sell_price1 - put_buy_price1)
                    
                profit1 = call_profit1 + put_profit1
                # profit_list.append(profit)
                min_profit1 = min(min_profit1,profit1)
                max_profit1 = max(max_profit1,profit1)
                
                if((call_buy_price1 >call_sell_price1*(1+strategy_dict[strrat_1]["SL_percent"])) & (call_position_active1 == True) & (strategy_dict[strrat_1]["stop_loss_percent"] == True)):
                    call_position_active1 = False
                    trade_type1 = "Stoploss_Call"
                    final_call_buy1 = call_buy_price1
                    final_call_profit1 = call_profit1
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], call_sell_price1, 0, index_,future_price_end, end_atm_IV,call_buy_price1, 0,min_profit1,max_profit1,trade_type1])
    
                if((put_buy_price1 > put_sell_price1*(1+strategy_dict[strrat_1]["SL_percent"])) & (put_position_active1 == True) & (strategy_dict[strrat_1]["stop_loss_percent"] == True)):
                    put_position_active1 = False
                    trade_type1 = "Stoploss_put"
                    final_put_buy1 = put_buy_price1
                    final_put_profit1 = put_profit1
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], 0, put_sell_price1, index_,future_price_end, end_atm_IV,0, put_buy_price1,min_profit1,max_profit1,trade_type1])
                
                if((index_ == strategy_dict[strrat_1]["end_time"]) & ((call_position_active1 == True) | (put_position_active1 == True))):
                    future_price_end = df_weekly_futures_prices.loc[index_]
                    end_atm_strike = round(future_price_end / roundoff_factor) * roundoff_factor
                    end_atm_IV = df_weekly_futures[str(end_atm_strike) + "_IV"].loc[index_]
                    
                    if(call_position_active1 == True):
                        call_position_active1 = False
                        trade_type1 = "EndTime_Call"
                        final_call_buy1 = call_buy_price1
                        final_call_profit1 = call_profit1
                        transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], call_sell_price1, 0, index_,future_price_end, end_atm_IV,call_buy_price1, 0,min_profit1,max_profit1,trade_type1])
    
                    if(put_position_active1 == True):
                        put_position_active1 = False
                        trade_type1 = "EndTime_put"
                        final_put_buy1 = put_buy_price1
                        final_put_profit1 = put_profit1
                        transactionbook1.append([date, date_name,expiry_date, strategy_dict[strrat_1]["start_time"], future_price1, call_file_name[:-10], put_file_name[:-10], 0, put_sell_price1, index_,future_price_end, end_atm_IV,0, put_buy_price1,min_profit1,max_profit1,trade_type1])
    
                    break
    transactionbook_df1 = pd.DataFrame(transactionbook1[1:], columns = transactionbook1[0])
    transactionbook_df1["Call_Profit"] = transactionbook_df1['call_sell_price'] - transactionbook_df1['call_buy_price']
    transactionbook_df1["Put_Profit"] = transactionbook_df1['put_sell_price'] - transactionbook_df1['put_buy_price']
    transactionbook_df1["Total_Profit"] = transactionbook_df1["Call_Profit"] + transactionbook_df1["Put_Profit"]
    transactionbook_df1.to_csv(r"/Users/bnsl.j3/Desktop/Jatin Bansal/Options/OptionsCode/res/14Leg_Output_"+strrat_1+'.csv')
