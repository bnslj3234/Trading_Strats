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
date_details = pd.read_csv("BackTest_Dates_SMA.csv", header = 0).dropna()
weeklist = date_details["Week"].unique().tolist()
# date_list = date_details["Date"].tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] == "Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] == "Wednesday"].tolist()
# wed_thu_hol = holidays_list[(holidays_list["Day"] == "Thursday") | (holidays_list["Day"] == "Wednesday")]["Date"].tolist()
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'E:/Nifty Output/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path = "E:/"
instrument ="NIFTY"

# instrument ="NIFTY"
if instrument =="BANKNIFTY":
    roundoff_factor = 100
    start_time ="09:20:00"
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
    
transactionbook = [["Date", "Date_name","expiry_date", "start_time", "future_price", "min_average_price",
                    "max_average_price","Call_Ticker", "Put_Ticker","call_sell_price", "put_sell_price", 
                    "end_time","call_buy_price", "put_buy_price", "min_profit","max_profit",]]

dfavg =pd.read_csv("BankNiftyDataNew.csv", index_col="Date")   
dfavg["200SMA"] = dfavg["Price"].rolling(200).mean()
dfavg["50SMA"] = dfavg["Price"].rolling(50).mean()
dfavg["100SMA"] = dfavg["Price"].rolling(100).mean()
dfavg["150SMA"] = dfavg["Price"].rolling(150).mean()
MIN = 100000000
MAX = -100000000  

# date_list = ["08-11-2021","09-11-2021","10-11-2021","11-11-2021"]
'''for each date we put check if we have expiry date in datelist'''
for w in weeklist:
    # w = "week2"
    date_list = date_details["Date"][date_details["Week"] == w].tolist()
    for date in date_list:
        if get_expiry_date(date) not in date_list:
            print("Expiry date "+ get_expiry_date(date) +" for : " +date+ " is not present in datelist. Please add it")
    # ,"05-02-2021", "12-02-2021","19-02-2021"
    put_sell_dict = {}
    call_sell_dict = {}
    all_new_data = pd.DataFrame()
    for date in date_list:
        # if pd.to_datetime(date, format = "%d-%m-%Y").strftime("%A")
        folder_name, folder_name_ = get_folder_name(date)
        month_name=pd.to_datetime(date, format = "%d-%m-%Y").strftime("%B")
        date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
        dir_1=changing_path + date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
        to_zip=dir_1+folder_name[:-1]+str(".zip")
        zf1 = zipfile.ZipFile(to_zip)
        expiry_date = get_expiry_date(date)  
        expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
        expiry_date_name = pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%A")
        weekly_futures_filename = path_for_weekly_futures + "/" + month_name[0:3]+ "'"+date[-2:] + "/"+ pd.to_datetime(date , format = '%d-%m-%Y').strftime("%d%m%Y") + "_results.csv"
        df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
        wfut_cols = [x for x in df_weekly_futures.columns if "WFUT" in x]
        future_prices_column = df_weekly_futures[["Time",wfut_cols[0]]]
        future_prices_column.set_index("Time", inplace = True)
        future_price = future_prices_column.loc[start_time].values[0]

        df_weekly_futures.set_index("Time", inplace = True)
        print("working on "+date + " with expiry : "+expiry_date)

        '''Get expiry date and then get file for both and call option for their respective Strike price'''
        
        min_average_price = min(dfavg["50SMA"].loc[date],dfavg["100SMA"].loc[date],dfavg["150SMA"].loc[date],dfavg["200SMA"].loc[date])
        max_average_price = max(dfavg["50SMA"].loc[date],dfavg["100SMA"].loc[date],dfavg["150SMA"].loc[date],dfavg["200SMA"].loc[date])
        # put_sell_price = "Nan"
        # call_sell_price = "Nan"
        if future_price > max_average_price:
            working_strike = round(min_average_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike
            put_strike = working_strike
            # put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option = pd.DataFrame()
            while df_put_option.empty == True:
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                try:
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                except:
                    put_strike = put_strike + 100
            # df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            try:
                df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
            except:
                df_call_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
            
            time_temp = get_data(df_put_option, df_call_option)
            put_sell_price = time_temp["Put_BuyPrice"].loc[start_time]
            put_sell_dict[put_file_name[:-8]+ "_"+date] = [put_sell_price,MIN,MAX,0]
            transactionbook.append([date, date_name,expiry_date, start_time, future_price,min_average_price,max_average_price, np.nan, put_file_name[:-8], np.nan, put_sell_price, np.nan,np.nan, np.nan,0,0])
        
        elif future_price < min_average_price:
            working_strike = round(max_average_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike
            put_strike = working_strike
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            # call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            # df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            # df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
            df_call_option = pd.DataFrame()
            while df_call_option.empty == True:
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                try:
                    df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                except:
                    call_strike = call_strike - 100
            
            try:
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            except:
                df_put_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
            
        
            time_temp = get_data(df_put_option, df_call_option)
            call_sell_price = time_temp["Call_BuyPrice"].loc[start_time]
            call_sell_dict[call_file_name[:-8]+ "_"+date] = [call_sell_price,MIN,MAX,0]
            transactionbook.append([date, date_name,expiry_date, start_time, future_price,min_average_price,max_average_price, call_file_name[:-8], np.nan, call_sell_price, np.nan, np.nan,np.nan, np.nan,0,0])
    
        elif (future_price > min_average_price) and (future_price < max_average_price):
            working_strike = round(min_average_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike
            put_strike = working_strike
            df_put_option = pd.DataFrame()
            while df_put_option.empty == True:
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
                try:
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
                except:
                    put_strike = put_strike + 100
            # put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            # df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            try:
                df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
            except:
                df_call_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
            
        
            time_temp = get_data(df_put_option, df_call_option)
            put_sell_price = time_temp["Put_BuyPrice"].loc[start_time]
            put_sell_dict[put_file_name[:-8]+ "_"+date] = [put_sell_price,MIN,MAX,0]
            transactionbook.append([date, date_name,expiry_date, start_time, future_price,min_average_price,max_average_price, np.nan, put_file_name[:-8], np.nan, put_sell_price, np.nan,np.nan, np.nan,0,0])
            
            working_strike = round(max_average_price / roundoff_factor) * roundoff_factor
            call_strike = working_strike
            put_strike = working_strike
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            # call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            df_call_option = pd.DataFrame()
            while df_call_option.empty == True:
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
                try:
                    df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
                except:
                    call_strike = call_strike - 100
                
            try:
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            except:
                df_put_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
            
            # df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
        
            time_temp = get_data(df_put_option, df_call_option)
            
            call_sell_price = time_temp["Call_BuyPrice"].loc[start_time]
            call_sell_dict[call_file_name[:-8]+ "_"+date] = [call_sell_price,MIN,MAX,0]
            transactionbook.append([date, date_name,expiry_date, start_time, future_price,min_average_price,max_average_price, call_file_name[:-8], np.nan, call_sell_price, np.nan, np.nan,np.nan, np.nan,0,0])
    
        
        # transactionbook.append([date, date_name,expiry_date, start_time, future_price,min_average_price,max_average_price, call_file_name[:-10], put_file_name[:-10], call_sell_price, put_sell_price, index_,np.nan, np.nan,0,0])
        print(call_sell_dict,put_sell_dict)
        print("Call/Put Sell Done. Getting all data for that date")
        for key in call_sell_dict:
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(key[-18:-13])+str("CE.NFO.csv")
            
            # df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
            try:
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            except:
                df_put_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
            
        
            new_temp_data = get_data(df_put_option, df_call_option)
            new_temp_data.columns = [key[-18:-13]+"_"+date+"_"+x for x in new_temp_data.columns]
            # if 
            all_new_data = pd.concat([all_new_data,new_temp_data], axis = 1)
        
        for key in put_sell_dict:
            put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(key[-18:-13])+str("PE.NFO.csv")
            call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
            
            df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_name))
            # df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
            try:
                df_call_option = pd.read_csv(zf1.open(folder_name_+call_file_name))
            except:
                df_call_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
        
            new_temp_data = get_data(df_put_option, df_call_option)
            new_temp_data.columns = [key[-18:-13]+"_"+date+"_"+x for x in new_temp_data.columns]
            all_new_data = pd.concat([all_new_data,new_temp_data], axis = 1)
        
        print("Cal/Put Sell Done. Now checking for max/min stoploss")
        # all_new_data = all_new_data[all_new_data.columns.unique()]
        all_new_data = all_new_data.loc[:,~all_new_data.columns.duplicated()].copy()
        for index_ in time_temp[time_temp.index >= start_time].index.tolist():
    
            for key in call_sell_dict:

                call_sell_dict[key][3] = all_new_data[key[-18:-13]+"_"+date+"_Call_SellPrice"].loc[index_]
                # call_sell_dict[key][3] = new_temp_data["Call_SellPrice"].loc[index_]
                profit = (call_sell_price - call_sell_dict[key][3])
                call_sell_dict[key][1] = min(call_sell_dict[key][1],profit)
                call_sell_dict[key][2] = max(call_sell_dict[key][2], profit)
                if((date_name == expiry_date_name) & (index_ == end_time)):
                    transactionbook.append([date, date_name,expiry_date, np.nan, np.nan,np.nan,np.nan, key[:-11], np.nan, np.nan, np.nan, index_,call_sell_dict[key][3], np.nan,call_sell_dict[key][1],call_sell_dict[key][2]])
            
            for key in put_sell_dict:

                put_sell_dict[key][3] = all_new_data[key[-18:-13]+"_"+date+"_Put_SellPrice"].loc[index_]
                # put_buy_price = time_temp[str(working_strike) + "P_S"].loc[index_]
                profit = (put_sell_price - put_sell_dict[key][3])
                put_sell_dict[key][1] = min(put_sell_dict[key][1],profit)
                put_sell_dict[key][2] = max(put_sell_dict[key][2], profit)
                if((date_name == expiry_date_name) & (index_ == end_time)):
                    transactionbook.append([date, date_name,expiry_date, np.nan, np.nan,np.nan,np.nan, np.nan,key[:-11], np.nan, np.nan, index_,np.nan, put_sell_dict[key][3],put_sell_dict[key][1],put_sell_dict[key][2]])
        
transaction_book_df = pd.DataFrame(transactionbook[1:], columns = transactionbook[0])
transaction_book_df.to_csv("SMA_Output.csv", index = False)
# dfavg =pd.read_csv("BankNiftyData.csv", index_col="Date", parse_dates=(True))
# dfavg.sort_index(inplace = True)
# dfavg[]
    