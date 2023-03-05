# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 20:25:29 2022

@author: Jatin
"""

import pandas as pd
import numpy as np
import datetime
# import matplotlib.pyplot as plt
from datetime import timedelta
import datetime as dt
# import os
# import math
# import zipfile

def get_next_day(date, get_day):
    # today_ = datetime()
    date_ = pd.to_datetime(date, format ="%d-%m-%Y")
    if get_day == 'T':
        thursday = date_ + dt.timedelta( (3-date_.weekday()) % 7 )
        return thursday.strftime("%d-%m-%Y")
    if get_day == 'W':
        wednesday = date_ + dt.timedelta( (2-date_.weekday()) % 7 )
        return wednesday.strftime("%d-%m-%Y")

def get_expiry_date(date_str):
    
    if get_next_day(date_str, 'T') in Thur_Hols:
        expiry_date = get_next_day(date_str, 'W')
    else:
        expiry_date = get_next_day(date_str, 'T')
    return expiry_date
    
def check_stoploss(entry_price,current_price, position, stop_loss_percent):
    if position =="Long":
        if current_price < (1-stop_loss_percent)*entry_price:
            return True
        else:
            return False
    elif position =="Short":
        if current_price > (1+stop_loss_percent)*entry_price:
            return True
        else:
            return False
def get_bands(future_price, dailyvix):
    upper_band = future_price*np.exp(dailyvix)
    lower_band = future_price*np.exp(-1*dailyvix)
    return upper_band, lower_band

# def get_call_put_atm_df(index,expiry_date, strike_price = None):
#     # df_weekly_futures
#     expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
#     # time_temp=pd.read_csv("TimeTemplate.csv")
#     df_weekly_futures_used = df_weekly_futures.iloc[:,[0,7]]
#     # df_weekly_futures_used = df_weekly_futures[['Time' ,wfut_cols[0] ]].copy()
#     data_futures=df_weekly_futures_used.drop_duplicates(["Time"])
#     data_futures=data_futures.fillna(method="bfill")
#     time_temp["Futures_Price"] = data_futures.iloc[:,1]
#     time_temp.set_index("Time", inplace = True)
#     if index != None:
#         future_price = time_temp['Futures_Price'].loc[index]
#         working_strike = round(future_price / roundoff_factor) * roundoff_factor
        
#     if strike_price == None:
#         call_strike = working_strike + otm_value_wed_thu
#         put_strike = working_strike - otm_value_wed_thu
#     else:
#         working_strike = strike_price
#         call_strike = working_strike + otm_value_wed_thu
#         put_strike = working_strike - otm_value_wed_thu
        
#     put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
#     call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
#     df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
#     df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
#     data_put_atm=df_put_option.drop_duplicates(["Time"])
#     data_put_atm.set_index("Time", inplace = True)
#     time_temp[put_file_name[:-8]+"_LTP"] = data_put_atm["LTP"]
#     time_temp[put_file_name[:-8]+"_BuyPrice"] = data_put_atm["BuyPrice"]
#     time_temp[put_file_name[:-8]+"_SellPrice"] = data_put_atm["SellPrice"]
    
#     data_call_atm=df_call_option.drop_duplicates(["Time"])
#     data_call_atm.set_index("Time", inplace = True)
#     time_temp[call_file_name[:-8]+"_LTP"] = data_call_atm["LTP"]
#     time_temp[call_file_name[:-8]+"_BuyPrice"] = data_call_atm["BuyPrice"]
#     time_temp[call_file_name[:-8]+"_SellPrice"] = data_call_atm["SellPrice"]
#     time_temp=time_temp.fillna(method="bfill")
    # if index!= None:
    #     return time_temp,put_file_name,call_file_name,future_price
    # else:
    #     return time_temp,put_file_name,call_file_name

def get_call_put_atm_df(df_weekly_futures,index,expiry_date,strike_price = None):
   df_weekly_futures_used = df_weekly_futures.iloc[:,[0,7]]
   data_futures=df_weekly_futures_used.drop_duplicates(["Time"])
   data_futures=data_futures.fillna(method="bfill")
   data_futures.set_index("Time", inplace = True)
   df_weekly_futures_new = df_weekly_futures.set_index("Time").copy()
   if index != None:
       future_price = data_futures.loc[index].values[0]
       working_strike = round(future_price / roundoff_factor) * roundoff_factor
       
   if strike_price == None:
       call_strike = working_strike + otm_value_wed_thu
       put_strike = working_strike - otm_value_wed_thu
   else:
       working_strike = strike_price
       call_strike = working_strike + otm_value_wed_thu
       put_strike = working_strike - otm_value_wed_thu
       
   put_columns = [x for x in df_weekly_futures_new.columns if str(put_strike)+'P' in x]
   call_columns = [x for x in df_weekly_futures_new.columns if str(call_strike)+'C' in x]
   # fut_columns = [str(put_strike)+"WFUT", str(call_strike)+"WFUT"]
   data_call_put = df_weekly_futures_new[put_columns + call_columns]
   data_call_put["Futures_Price"] = df_weekly_futures_new[str(working_strike) + 'WFUT']
   # data_call = df_weekly_futures[call_columns]
   # return data_call_put, put_strike, call_strike
   if index!= None:
       return data_call_put, put_strike, call_strike,future_price
   else:
       return data_call_put, put_strike, call_strike


stoploss_percent = 0.20
stoploss_percent_combined = 0.01
instrument ="BANKNIFTY"

# instrument ="NIFTY"
if instrument =="BANKNIFTY":
    roundoff_factor = 100
    start_time ="09:20:00"
    end_time ="15:00:00"
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


# start_time_dt = datetime.datetime.strptime(start_time,"%H:%M:%S").time()
# end_time_dt=datetime.datetime.strptime(end_time,"%H:%M:%S").time()

date_list = pd.read_csv("Backtest_Dates.csv", header = 0)["Date"].dropna().tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] =="Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] =="Wednesday"].tolist()
vixdf = pd.read_csv("Vix.csv", index_col ="Date")
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'C:/Users/Jatin/Downloads/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path ="C:/Users/Jatin/Downloads/Compressed/"
# day_profit = {}
# date_list = ["01-11-2021","02-11-2021","08-11-2021","09-11-2021","10-11-2021","11-11-2021","15-11-2021","16-11-2021"]
date_list = ["01-11-2021","02-11-2021","03-11-2021","08-11-2021","09-11-2021","10-11-2021","11-11-2021"]
# date_list = ["02-02-2021","03-02-2021","04-02-2021"]
put_qty = 0
call_qty = 0
future_price =0
'''Will have to initiate atleast one of them as 1. Here we are taking a initial 
view on market'''
put_sell_signal = 0
call_sell_signal = 1
sell_price_call = 0
sell_price_put = 0
total_transactions = 0
call_file_name = ''
put_file_name = ''
put_strike = 0
call_strike = 0
transactions_book = [["Date", 'Day',"Time","FuturesPrice",'Upper_Band','Lower_Band','Instrument_Name', 'BuyPrice', 'SellPrice', 'BuyQty','SellQty',"Profit","trade_type"]]

for date in date_list:
    # date = '11-11-2021'
    # print(date)
    # if pd.to_datetime(date, format ="%d-%m-%Y")>=pd.to_datetime("01-02-2022", format ="%d-%m-%Y"):
    #     folder_name="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
    #     folder_name_ ="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/Options'+'/'
    # else:
    #     folder_name="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
    #     folder_name_ ="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
    # finding the month name
    month_name=pd.to_datetime(date, format ="%d-%m-%Y").strftime("%B")
    # dir_1=changing_path + date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    #Now finding the file_name that needs to be opened
    # to_zip=dir_1+folder_name[:-1]+str(".zip")
    # zf = zipfile.ZipFile(to_zip)
    
    '''read Futures file for that day. took future's price as of start_time to calculate ATM'''
    weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+date[-2:] +"/"+ pd.to_datetime(date , format = '%d-%m-%Y').strftime("%d%m%Y") +"_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    # wfut_cols = [x for x in df_weekly_futures.columns if"WFUT"in x]
    # future_price = df_weekly_futures[wfut_cols[0]][df_weekly_futures["Time"] == start_time].values[0]
    # weekly_futures_filename = path_for_weekly_futures + "/" + month_name[0:3]+ "'"+date[-2:] + "/"+ pd.to_datetime(date , format = '%d-%m-%Y').strftime("%d%m%Y") + "_results.csv"
    # df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    # wfut_cols = [x for x in df_weekly_futures.columns if "WFUT" in x]
    # future_price = df_weekly_futures[wfut_cols[0]][df_weekly_futures["Time"] == start_time].values[0]
    
    check_combined_stoploss = False
    otm_value_wed_thu = 0

    # if pd.to_datetime(date).strftime("%A") in ['Thursday', 'Wednesday']:
    #     check_combined_stoploss = True
    #     otm_value_wed_thu = 100
    
    '''Get expiry date and then get file for both and call option for their respective Strike price'''
    dailyvix = vixdf.loc[date].values[0]*0.01/np.sqrt(252)
    expiry_date = get_expiry_date(date)
    
    if(call_qty!=0):
        print("Call position from previous day getting prices for "+(call_file_name[16:21]) +"CE")
        # print("Now working on "+ put_file_name +" "+call_file_name)
        upper_band, lower_band = get_bands(future_price, dailyvix)
        # upper_band = future_price*np.exp(dailyvix)
        # lower_band = future_price*np.exp(-1*dailyvix)
        print(date,"Now working on "+ str(put_strike) +" "+str(call_strike),"from previous day. call range after adjusting to vix for next day:",upper_band, lower_band,"Future at :",future_price)
        # time_temp,put_file_name,call_file_name = get_call_put_atm_df(None, expiry_date,int(call_file_name[16:21]))
        data_call_put, put_strike, call_strike = get_call_put_atm_df(df_weekly_futures,None,expiry_date,call_strike)
    if(put_qty!=0):
        print("Put position from previous day getting prices for "+(put_file_name[16:21]) +"PE")
        upper_band, lower_band = get_bands(future_price, dailyvix)
        # upper_band = future_price*np.exp(dailyvix)
        # lower_band = future_price*np.exp(-1*dailyvix)
        print(date,"Now working on "+ str(put_strike) +" "+str(call_strike),"from previous day. put range after adjusting to vix for next day:",upper_band, lower_band,"Future at :",future_price)
        # time_temp,put_file_name,call_file_name = get_call_put_atm_df(None,expiry_date,int(put_file_name[16:21]))
        data_call_put, put_strike, call_strike = get_call_put_atm_df(df_weekly_futures,None,expiry_date,put_strike)


    # expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    
    # working_strike = round(future_price / roundoff_factor) * roundoff_factor
    # call_strike = working_strike + otm_value_wed_thu
    # put_strike = working_strike - otm_value_wed_thu
    # put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
    # call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
    
    # df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    # df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
    for index_ in df_weekly_futures.Time[(df_weekly_futures.Time >= start_time) & (df_weekly_futures.Time <= end_time)]:
    # for index_,row in time_temp[(time_temp.index >= start_time) & (time_temp.index <= end_time)].iterrows():
        
        '''Generally Condition Will be true at t == 0'''
        if((put_qty == 0) & (call_qty == 0)):
            '''we will take a position'''
            # future_price = df_weekly_futures_used[wfut_cols[0]][df_weekly_futures_used["Time"] == start_time].values[0]
            # time_temp,put_file_name,call_file_name,future_price = get_call_put_atm_df(df_weekly_futures,index_,expiry_date)
            data_call_put, put_strike, call_strike,future_price = get_call_put_atm_df(df_weekly_futures,index_,expiry_date)
            # print()
            if(put_sell_signal == 1):
                sell_price_put = data_call_put[str(put_strike)+"P_B"].loc[index_]
                # sell_price_put = time_temp[put_file_name[:-8]+"_BuyPrice"].loc[index_]
                put_qty = -1
                total_transactions+=1
                trade_type = 'Put_Sell'
                # print(trade_type)
                upper_band, lower_band = get_bands(future_price, dailyvix)
                # upper_band = future_price*np.exp(dailyvix)
                # lower_band = future_price*np.exp(-1*dailyvix)  
                # transactions_book.append([date,date_name,index_,future_price,upper_band,lower_band,put_file_name[:-8],0,sell_price_put,0,put_qty,0,trade_type])
                transactions_book.append([date,date_name,index_,future_price,upper_band,lower_band,put_strike,0,sell_price_put,0,put_qty,0,trade_type])
                put_sell_signal == 0
                print(date,index_,trade_type,"First order hit for :",str(put_strike),"at :",sell_price_put,"Futures at :", future_price)
                print(date,"Range after first entry trade :",upper_band, lower_band,"Future at :",future_price)
            if(call_sell_signal == 1):
                sell_price_call = data_call_put[str(call_strike)+"P_B"].loc[index_]
                # sell_price_call = time_temp[call_file_name[:-8]+"_BuyPrice"].loc[index_]
                call_qty = -1
                trade_type = 'Call_Sell'
                upper_band, lower_band = get_bands(future_price, dailyvix)
                # upper_band = future_price*np.exp(dailyvix)
                # lower_band = future_price*np.exp(-1*dailyvix)
                transactions_book.append([date,date_name,index_, future_price,upper_band,lower_band,call_strike,0,sell_price_call,0,call_qty,0,trade_type])
                # transactions_book.append([date,date_name,index_, future_price,upper_band,lower_band,call_file_name[:-8],0,sell_price_call,0,call_qty,0,trade_type])
                total_transactions+=1
                call_sell_signal == 0
                print(date,index_,trade_type,"First order hit for :",call_strike,"at :", sell_price_call,"Futures at :", future_price)
                print(date,"Range after first entry trade :",upper_band, lower_band,"Future at :",future_price)

            # upper_band = future_price*np.exp(dailyvix)
            # lower_band = future_price*np.exp(-1*dailyvix)  
            # print(date,"Range after first entry trade :",upper_band, lower_band,"Future at :",future_price)
        '''We will get volatility bands here'''
        # if put_qty!=0:
        
        
        '''Should we compare spot or futures with upper and lower bands'''
        if(index_ <= last_trade_open_time):
            # print("Check Roll over")
            current_future_price = df_weekly_futures[df_weekly_futures["Time"]== index_].iloc[:,7].values[0]
            # if time_temp['Futures_Price'].loc[index_] > upper_band:
            # print(date, index_, current_future_price, upper_band, lower_band)
            if (current_future_price > upper_band):
                # print(date,"Check Upper Band")
                if (put_qty !=0) :    
                    # buy_price_put = time_temp[put_file_name[:-8]+"_SellPrice"].loc[index_]
                    buy_price_put = data_call_put[str(put_strike)+"P_S"].loc[index_]

                    put_qty = -1*put_qty
                    total_transactions+=1
                    profit = sell_price_put - buy_price_put
                    trade_type = 'Put_BuyRU'
                    print(date,index_,trade_type,"Upper band limit exceed :",upper_band,"Fututres Price :", current_future_price,"put bought back at :", buy_price_put)
                    # transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,put_file_name[:-8],buy_price_put,0,put_qty,0,profit,trade_type])
                    transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,put_strike,buy_price_put,0,put_qty,0,profit,trade_type])
                    put_qty = 0
                    
                if (call_qty !=0):
                    # buy_price_call = time_temp[call_file_name[:-8]+"_SellPrice"].loc[index_]
                    buy_price_call = data_call_put[str(call_strike)+"C_S"].loc[index_]
                    call_qty = -1*call_qty
                    total_transactions+=1
                    profit = sell_price_call - buy_price_call
                    trade_type = 'Call_BuyRU'
                    print(date,index_,trade_type,"Upper band limit exceed :", upper_band,"Fututres Price :", current_future_price,"call bought back at :", buy_price_call)
                    # transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,call_file_name[:-8],buy_price_call,0,call_qty,0,profit,trade_type])
                    transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,call_strike,buy_price_call,0,call_qty,0,profit,trade_type])
                    call_qty = 0
                    
                '''I have closed my previous positions. I'll sell put of current ATM now as
                market is upward trending'''
                data_call_put, put_strike, call_strike,future_price = get_call_put_atm_df(df_weekly_futures,index_,expiry_date)
                sell_price_put = data_call_put[str(put_strike)+"P_B"].loc[index_]
                # sell_price_put = time_temp[put_file_name[:-8]+"_BuyPrice"].loc[index_]
                put_qty = -1
                upper_band, lower_band = get_bands(future_price, dailyvix)
                # upper_band = future_price*np.exp(dailyvix)
                # lower_band = future_price*np.exp(-1*dailyvix)
                trade_type = 'Put_SellRUA'
                print(date,index_,"Rollover done Put sold at :", sell_price_put,"new strike price is :", put_file_name,"Futures at :", data_call_put["Futures_Price"].loc[index_])
                transactions_book.append([date,date_name,index_,future_price,upper_band,lower_band,put_strike,0,sell_price_put,0,put_qty,0,trade_type])
                total_transactions+=1
                print(date,index_,trade_type,"range after rollover with upper band :",upper_band, lower_band,"Future at :",future_price)

            # elif(time_temp['Futures_Price'].loc[index_] < lower_band):
            elif(current_future_price < lower_band):
                # print("Check Lower band")
                if (put_qty !=0):
                    # buy_price_put = time_temp[put_file_name[:-8]+"_SellPrice"].loc[index_]
                    buy_price_put = data_call_put[str(put_strike)+"P_S"].loc[index_]
                    put_qty = -1*put_qty
                    total_transactions+=1
                    profit = sell_price_put - buy_price_put
                    trade_type = 'Put_BuyRL'
                    print(date,index_,trade_type,"lower band limit exceed :", lower_band,"Fututres Price :", current_future_price,"put bought back at :", buy_price_put)
                    transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,put_strike,buy_price_put,0,put_qty,0,profit,trade_type])
                    put_qty = 0
                    
                if (call_qty !=0):
                    # break
                    # buy_price_call = time_temp[call_file_name[:-8]+"_SellPrice"].loc[index_]
                    buy_price_call = data_call_put[str(call_strike)+"C_S"].loc[index_]
                    call_qty = -1*call_qty
                    total_transactions+=1
                    profit = sell_price_call - buy_price_call
                    trade_type = 'Call_BuyRL'
                    print(date,index_,trade_type,"lower band limit exceed :", lower_band,"Fututres Price :", current_future_price,"call bought back at :", buy_price_call)
                    transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,call_strike,buy_price_call,0,call_qty,0,profit,trade_type])
                    call_qty = 0
                '''I have closed my previous positions. I'll sell call of current ATM now as
                market is downward trending'''
                data_call_put, put_strike, call_strike,future_price = get_call_put_atm_df(df_weekly_futures,index_,expiry_date)
                
                sell_price_call = data_call_put[str(call_strike)+"P_B"].loc[index_]
                # sell_price_call = time_temp[call_file_name[:-8]+"_BuyPrice"].loc[index_]
                call_qty = -1
                trade_type = 'Call_SellRLA'
                upper_band, lower_band = get_bands(future_price, dailyvix)
                # upper_band = future_price*np.exp(dailyvix)
                # lower_band = future_price*np.exp(-1*dailyvix)  
                print(date,index_,"Rollover done Call sold at :", sell_price_call,"new strike price is :", call_file_name,"Futures at :", future_price)
                transactions_book.append([date,date_name,index_,future_price,upper_band,lower_band,call_strike, 0,sell_price_call,0,call_qty,0,trade_type])
                total_transactions+=1
                print(date,index_,trade_type,"range after rollover with lower band :",upper_band, lower_band,"Future at :",future_price)
        
        elif((date_name == "Thursday") & (index_ >= end_time)):
            current_future_price = df_weekly_futures[df_weekly_futures["Time"] == index_].iloc[:,7].values[0]
            new_expiry = get_expiry_date(pd.to_datetime(expiry_date, format = "%d-%m-%Y") + timedelta(days=1))
            if(put_qty!=0):
                '''Close existing put position to rollover'''
                # buy_price_put = time_temp[put_file_name[:-8]+"_SellPrice"].loc[index_]
                buy_price_put = data_call_put[str(put_strike)+"P_S"].loc[index_]
                put_qty = -1*put_qty
                total_transactions+=1
                profit = sell_price_put - buy_price_put
                trade_type = 'Put_BuyRT'
                print(date,index_,trade_type,str(put_strike),"put Rollover for next thursday Fututres Price :", current_future_price,"put rolled at :", buy_price_put)
                transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,put_strike,buy_price_put,0,put_qty,0,profit,trade_type])
                # put_qty = 0
                '''Open put sell position with same strike for next expiry'''
                
                data_call_put, put_strike, call_strike,future_price = get_call_put_atm_df(index_,new_expiry, put_strike)
                
                sell_price_put = data_call_put[str(put_strike)+"P_B"].loc[index_]
                # sell_price_put = time_temp[put_strike+"_BuyPrice"].loc[index_]
                put_qty = -1
                trade_type = 'Put_SellRT'
                # upper_band, lower_band = get_bands(future_price, dailyvix)
                # upper_band = future_price*np.exp(dailyvix)
                # lower_band = future_price*np.exp(-1*dailyvix)
                print(date,index_,"Rollover done on Thursday Put sold at :", sell_price_put,"new strike price is :", put_file_name,"Futures at :", future_price)
                transactions_book.append([date,date_name,index_,future_price,upper_band,lower_band,put_strike,0,sell_price_put,0,put_qty,0,trade_type])
                total_transactions+=1
                print(date,index_,trade_type,"range after rollover ",upper_band, lower_band,"Future at :",future_price)

            if(call_qty!=0):
                '''Close existing call position to rollover'''
                # buy_price_call = time_temp[call_file_name[:-8]+"_SellPrice"].loc[index_]
                buy_price_call = data_call_put[str(call_strike)+"C_S"].loc[index_]
                call_qty = -1*call_qty
                total_transactions+=1
                profit = sell_price_call - buy_price_call
                trade_type = 'Call_BuyRT'
                print(date,index_,trade_type,call_strike,"call Rollover for next thursday Fututres Price :", current_future_price,"call rolled at :", buy_price_call)
                transactions_book.append([date,date_name,index_,current_future_price,upper_band, lower_band,call_strike,buy_price_call,0,call_qty,0,profit,trade_type])
                # call_qty = 0
                '''Open call sell position with same strike for next expiry'''
                
                data_call_put, put_strike, call_strike,future_price = get_call_put_atm_df(index_,new_expiry, call_strike)
                
                sell_price_call = data_call_put[str(call_strike)+"P_B"].loc[index_]
                # sell_price_call = time_temp[call_strike+"_BuyPrice"].loc[index_]
                call_qty = -1
                trade_type = 'Call_SellRT'
                # upper_band, lower_band = get_bands(future_price, dailyvix)
                # upper_band = future_price*np.exp(dailyvix)
                # lower_band = future_price*np.exp(-1*dailyvix)
                print(date,index_,"Rollover done Call sold  at :", sell_price_call,"new strike price is :", call_file_name,"Futures at :", future_price)
                transactions_book.append([date,date_name,index_,future_price,upper_band, lower_band,call_strike, 0,sell_price_call,0,call_qty,0,trade_type])
                total_transactions+=1
                  
                print(date,index_,trade_type,"range after rollover",upper_band, lower_band," Future at :",future_price)
        
        # if(call_qty!=0):
        #     # print("Check call stoploss")
        #     if((time_temp[call_file_name[:-8]+"_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_call)):
        #         index_c  = index_
        #         idx_c = np.searchsorted(time_temp.index, index_)
        #         call_qty = -1*call_qty
        #         total_transactions+=1
        #         buy_price_call = time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)]
        #         trade_type = 'Stoploss_C'
        #         profit = sell_price_call - buy_price_call
        #         transactions_book.append([date,date_name,index_,current_future_price, call_file_name[:-8],buy_price_call, 0,call_qty,0,profit,trade_type])
        #         call_qty = 0
        #         # print(trade_type)
        #         # max_loss =  max_loss + (sell_price_call-buy_price_call)
        #         print("Stop loss hit for call bought call option buying at :",time_temp.index[min(idx_c+1, len(time_temp)-1)],"for :",buy_price_call ,"making profit of :", (sell_price_call-buy_price_call))
            
            # elif(index_ == end_time):
            #     index_c  = index_
            #     idx_c = np.searchsorted(time_temp.index, index_)
            #     call_qty = -1*call_qty
            #     total_transactions+=1
            #     buy_price_call = time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)]
            #     print("Time Close hit for call option buying at :",time_temp.index[min(idx_c+1, len(time_temp)-1)],"for :",buy_price_call,"making profit of :", (sell_price_call-buy_price_call))
            #     trade_type = 'EndTime_C'
            #     profit = sell_price_call - buy_price_call
            #     print(trade_type)
            #     transactions_book.append([date,date_name,index_, call_file_name[:-8],buy_price_call, 0,call_qty,0,profit,trade_type])
            #     call_qty = 0
        
        # if(put_qty!=0):
        #     # print("Check Put stoploss")
        #     if( (time_temp[put_file_name[:-8]+"_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_put)):
        #         index_p  = index_
        #         idx_p = np.searchsorted(time_temp.index, index_)
        #         put_qty = -1*put_qty
        #         total_transactions+=1
        #         buy_price_put = time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)]
        #         trade_type = 'Stoploss_P'
        #         profit = sell_price_put - buy_price_put
        #         print(trade_type)
        #         transactions_book.append([date,date_name,index_,current_future_price, put_file_name[:-8],buy_price_put,0,put_qty,0,profit,trade_type])
        #         put_qty = 0
        #         # max_loss =  max_loss + (sell_price_put-buy_price_put)
        #         print("Stop loss hit for put bought put option buying at :",time_temp.index[min(idx_p+1, len(time_temp)-1)],"for :",buy_price_put ,"making profit of :", (sell_price_put-buy_price_put) )            
            
            # elif(index_ == end_time):
            #     index_p  = index_
            #     idx_p = np.searchsorted(time_temp.index, index_)
            #     put_qty = -1*put_qty
            #     buy_price_put = time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)]
            #     profit = sell_price_put - buy_price_put
            #     trade_type = 'EndTime_P'
            #     total_transactions+=1
            #     print(trade_type)
            #     transactions_book.append([date,date_name,index_, put_file_name[:-8],buy_price_put,0,put_qty,0,profit,trade_type])
            #     put_qty = 0
            #     print("Time close hit for put option buying at :",time_temp.index[min(idx_p+1, len(time_temp)-1)],"for :",buy_price_put ,"making profit of :", (sell_price_put-buy_price_put))
                
transactions_book_df = pd.DataFrame(transactions_book[1:],   columns = transactions_book[0])
# transactions_book_df.to_csv(output_path)