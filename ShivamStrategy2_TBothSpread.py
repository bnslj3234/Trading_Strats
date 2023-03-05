# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 20:25:29 2022

@author: Jatin
"""

import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta, TH, WE
from datetime import timedelta
import datetime as dt
import os
from tqdm import tqdm
import zipfile

def get_next_day(date, get_day):
    # today_ = datetime()
    date_ = pd.to_datetime(date, format ="%d-%m-%Y")
    if get_day == 'T':
        thursday = date_ + dt.timedelta( (3-date_.weekday()) % 7 )
        return thursday.strftime("%d-%m-%Y")
    elif get_day == 'W':
        wednesday = date_ + dt.timedelta( (2-date_.weekday()) % 7 )
        return wednesday.strftime("%d-%m-%Y")
    
def get_last_day(date, get_day):
    end_of_month = pd.to_datetime(date, format ="%d-%m-%Y") + relativedelta(day=31)
    if get_day == "T":
        last_thursday = end_of_month + relativedelta(weekday=TH(-1))
        return last_thursday.strftime("%d-%m-%Y")
    elif get_day == 'W':
        last_wednesday = end_of_month + relativedelta(weekday=WE(-1))
        return last_wednesday.strftime("%d-%m-%Y")
    
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
    upper_band1 = future_price*np.exp(dailyvix)
    lower_band1 = future_price*np.exp(-1*dailyvix)
    upper_band2 = upper_band1*np.exp(dailyvix)
    lower_band2 = lower_band1*np.exp(-1*dailyvix)
    return upper_band1,upper_band2, lower_band1,lower_band2

def get_folder_name(expiry_date):
    if pd.to_datetime(expiry_date, format ="%d-%m-%Y")>=pd.to_datetime("01-02-2022", format ="%d-%m-%Y"):
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/Options'+'/'
    else:
        folder_name="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
        folder_name_ ="GFDLNFO_TICK_"+expiry_date[:2]+expiry_date[3:5]+expiry_date[-4:]+'/'
    return folder_name, folder_name_

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
    time_temp = time_temp.fillna(0)
    return time_temp

def get_future_prices(expiry_date):
    month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    weekly_futures_filename = path_for_weekly_futures +"/"+ month_name[0:3]+"'"+expiry_date[-2:] +"/"+ pd.to_datetime(expiry_date , format = '%d-%m-%Y').strftime("%d%m%Y") +"_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    # df_weekly_futures.set_index("Time", inplace = True)
    # df_weekly_futures_prices = (df_weekly_futures["FUT_B"] + df_weekly_futures["FUT_S"])*0.5
    return df_weekly_futures


stoploss_percent = 0.20
stoploss_percent_combined = 0.01
instrument ="NIFTY"

# instrument ="NIFTY"
if instrument =="BANKNIFTY":
    roundoff_factor = 100
    start_time ="09:17:00"
    end_time ="15:20:00"
    last_trade_open_time ="15:00:00"
    contract_size = 25
    # prefix ="BN"
    # spot_file_name ="BANKNIFTY.csv"
elif instrument =="NIFTY":
    roundoff_factor = 50
    start_time ="09:17:00"
    end_time ="15:29:15"
    last_trade_open_time ="15:29:00"
    contract_size = 50

# start_time_dt = datetime.datetime.strptime(start_time,"%H:%M:%S").time()
# end_time_dt=datetime.datetime.strptime(end_time,"%H:%M:%S").time()

# date_list = pd.read_csv("Backtest_Dates_S.csv", header = 0)["Date"].dropna().tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] =="Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] =="Wednesday"].tolist()
vixdf = pd.read_csv("Vix.csv", index_col ="Date")
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'E:/Nifty Output/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path ="E:/"
# day_profit = {}
# date_list = ["01-11-2021","02-11-2021","08-11-2021","09-11-2021","10-11-2021","11-11-2021","15-11-2021","16-11-2021"]
date_list = ["24-06-2021","25-06-2021","28-06-2021","29-06-2021","30-06-2021","01-07-2021","02-07-2021","05-07-2021","06-07-2021","07-07-2021"]
# date_list = ["01-02-2021","02-02-2021","03-02-2021","04-02-2021","05-02-2021","08-02-2021","09-02-2021","10-02-2021","11-02-2021"]
# date_list = ["08-03-2021","09-03-2021","10-03-2021"]
put_qtyL = 0
call_qtyL = 0
future_price =0
ref_future_price = 0
otm_strikeCL = 0
otm_strikePL = 0
otm_strikePS = 0
otm_strikeCS = 0
'''Will have to initiate atleast one of them as 1. Here we are taking a initial view on market'''
put_buy_signal = 0
call_buy_signal = 1
spread_variant = 1
expiry_freq= "W"
total_transactions = 0
transactions_book = [["Date", 'Day',"Time","FuturesPrice","Ref_FuturePrice","vix",'Upper_Band2','Upper_Band1','Lower_Band1','Lower_Band2','Instrument_NameCL', 'BuyPriceCL','BuyQtyCL','Instrument_NameCS', 'SellPriceCS', 'SellQtyCS','Instrument_NamePL', 'BuyPricePL','BuyQtyPL','Instrument_NamePS', 'SellPricePS','SellQtyPS', 'SellPriceCL','BuyPriceCS', 'SellPricePL','BuyPricePS',"ProfitC","ProfitP","trade_type"]]

for date in date_list:
    print(date)
    folder_name, folder_name_ = get_folder_name(date)
    month_name=pd.to_datetime(date, format ="%d-%m-%Y").strftime("%B")
    dir_1=changing_path + date[-4:] +"/"+ month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    #Now finding the file_name that needs to be opened
    to_zip=dir_1+folder_name[:-1]+str(".zip")
    zf1 = zipfile.ZipFile(to_zip)
    
    df_weekly_futures = get_future_prices(date)
    wfut_cols = [x for x in df_weekly_futures.columns if"WFUT"in x]
    df_weekly_futures=df_weekly_futures.fillna(method="bfill")
    '''Weekly Futures Prices'''
    
    '''Monthly Future Prices'''
    # future_price = df_weekly_futures["FUT_B"][df_weekly_futures["Time"] == start_time].values[0]
    expiry_date = get_expiry_date(date, expiry_freq)
    expiry_month_name=pd.to_datetime(expiry_date, format ="%d-%m-%Y").strftime("%B")
    
    
    '''Get expiry date and then get file for both and call option for their respective Strike price'''
    dailyvix = vixdf.loc[date].values[0]*0.01/np.sqrt(252)

    if(call_qtyL!=0):
        upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(ref_future_price, dailyvix)
        put_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePL)+str("PE.NFO.csv")
        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
        call_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
        df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
        time_tempL = get_data(df_put_option,df_call_option)
        # otm_strikeS = round(upper_band2 / roundoff_factor) * roundoff_factor
        call_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
        df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
        put_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePS)+str("PE.NFO.csv")
        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
        time_tempS = get_data(df_put_option,df_call_option)
        
    elif(put_qtyL!=0):
        upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(ref_future_price, dailyvix)
        put_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePL)+str("PE.NFO.csv")
        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
        call_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
        df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
        time_tempL = get_data(df_put_option,df_call_option)
        # otm_strikeS = round(upper_band2 / roundoff_factor) * roundoff_factor
        call_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
        df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
        put_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePS)+str("PE.NFO.csv")
        df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
        time_tempS = get_data(df_put_option,df_call_option)
    
    future_price = df_weekly_futures[wfut_cols[1]][df_weekly_futures["Time"] == start_time].values[0]
    
    for index_ in tqdm(df_weekly_futures.Time[(df_weekly_futures.Time >= start_time) & (df_weekly_futures.Time <= end_time)]):
        # """Get Price Bands at every second"""
        # upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(future_price, dailyvix)
        '''Generally Condition Will be true at t == 0'''
        if((put_qtyL == 0) & (call_qtyL == 0)):
            '''we will take a position'''
            upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(future_price, dailyvix)
            if(put_buy_signal == 1):
                otm_strikePL = round(lower_band1 / roundoff_factor) * roundoff_factor
                put_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePL)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
                otm_strikeCL = round(upper_band2 / roundoff_factor) * roundoff_factor
                call_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
                
                time_tempL = get_data(df_put_option,df_call_option)
                buy_price_putL = time_tempL["Put_SellPrice"].loc[start_time]
                put_qtyL = 1
                buy_price_callL = time_tempL["Call_SellPrice"].loc[start_time]
                call_qtyL = 1
                
                
                if spread_variant == 1:
                    otm_strikeCS = round(upper_band1 / roundoff_factor) * roundoff_factor
                    call_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
                    otm_strikePS = round(lower_band2 / roundoff_factor) * roundoff_factor
                    put_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePS)+str("PE.NFO.csv")
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
                    df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
                    time_tempS = get_data(df_put_option,df_call_option)
                    sell_price_putS = time_tempS["Put_BuyPrice"].loc[start_time]
                    put_qtyS = -1
                    sell_price_callS = time_tempS["Call_BuyPrice"].loc[start_time]
                    call_qtyS = -1
                else:
                    sell_price_putS = np.nan
                    put_qtyS = np.nan
                    sell_price_callS = np.nan
                    call_qtyS = np.nan
                     
                total_transactions+=1
                trade_type = 'PS_BUY_CS_SELL'
                
                transactions_book.append([date,date_name,index_,future_price,future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],buy_price_callL,call_qtyL,call_file_nameS[:-8],sell_price_callS,call_qtyS,put_file_nameL[:-8],buy_price_putL,put_qtyL,put_file_nameS[:-8],sell_price_putS,put_qtyS,0,0,0,0,0,0,trade_type])
                put_buy_signal = 0 
                ref_future_price = future_price
                # print(date,index_,trade_type,"First order hit for :",str(put_file_nameL[:-8])," at : ",buy_price_putL, " and : ", put_file_nameS[:-8],"at :",sell_price_putS,"Futures at :", future_price)
                # print(date,"Range after first entry trade :",upper_band1, lower_band1,"Future at :",future_price)
            
            if(call_buy_signal == 1):
                otm_strikeCL = round(upper_band1 / roundoff_factor) * roundoff_factor
                call_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
                otm_strikePL = round(lower_band2 / roundoff_factor) * roundoff_factor
                put_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePL)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
                time_tempL = get_data(df_put_option,df_call_option)
                buy_price_callL = time_tempL["Call_SellPrice"].loc[start_time]
                call_qtyL = 1
                buy_price_putL = time_tempL["Put_SellPrice"].loc[start_time]
                put_qtyL = 1
                
                
                if spread_variant == 1:
                    otm_strikeCS = round(upper_band2 / roundoff_factor) * roundoff_factor
                    call_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
                    df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
                    otm_strikePS = round(lower_band1 / roundoff_factor) * roundoff_factor
                    put_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePS)+str("PE.NFO.csv")
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
                    
                    time_tempS = get_data(df_put_option,df_call_option)
                    sell_price_callS = time_tempS["Call_BuyPrice"].loc[start_time]
                    call_qtyS = -1
                    sell_price_putS = time_tempS["Put_BuyPrice"].loc[start_time]
                    put_qtyS = -1
                else:
                    sell_price_callS = np.nan
                    call_qtyS = np.nan
                    sell_price_putS = np.nan
                    put_qtyS =np.nan
                
                trade_type = 'CS_BUY_PS_SELL'
                
                transactions_book.append([date,date_name,index_,future_price,future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],buy_price_callL,call_qtyL,call_file_nameS[:-8],sell_price_callS,call_qtyS,put_file_nameL[:-8],buy_price_putL,put_qtyL,put_file_nameS[:-8],sell_price_putS,put_qtyS,0,0,0,0,0,0,trade_type])
                # transactions_book.append([date,date_name,index_, future_price,upper_band,lower_band,call_file_name[:-8],0,sell_price_call,0,call_qty,0,trade_type])
                # upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(future_price, dailyvix)
                total_transactions+=1
                call_buy_signal = 0
                ref_future_price = future_price
                # print(date,index_,trade_type,"First order hit for :",str(call_file_nameL[:-8])," at : ",buy_price_callL, " and : ", call_file_nameS[:-8],"at :",sell_price_callS,"Futures at :", future_price)
                # print(date,"Range after first entry trade :",upper_band1, lower_band1,"Future at :",future_price)
            
        if(index_ <= last_trade_open_time):
            # print("Check Roll over")
            current_future_price = df_weekly_futures[df_weekly_futures["Time"]== index_].iloc[:,7].values[0]
            # current_future_price = df_weekly_futures[df_weekly_futures["Time"]== index_].iloc[:,1].values[0]
 
            if (current_future_price > upper_band1):
                # print(date,"Check Upper Band")
                # if (put_qtyL !=0) : 
                #     sell_price_putL = time_tempL["Put_BuyPrice"].loc[index_]
                #     sell_price_callL = time_tempL["Call_BuyPrice"].loc[index_]
                #     put_qtyL = -1*put_qtyL
                #     call_qtyL = -1*call_qtyL
                #     if spread_variant == 1:
                #         buy_price_callS = time_tempS["Call_SellPrice"].loc[index_]
                #         call_qtyS = -1*call_qtyS
                #         buy_price_putS = time_tempS["Put_SellPrice"].loc[index_]
                #         put_qtyS = -1*put_qtyS
                #     else:
                #         buy_price_callS = np.nan
                #         buy_price_putS = np.nan
                #         put_qtyS = np.nan
                #         call_qtyS = np.nan
                    
                #     # put_qtyS = -1*put_qtyS
                #     total_transactions+=1
                #     profitC = (sell_price_callL + sell_price_callS) - (buy_price_callL + buy_price_callS)
                #     profitP = (sell_price_putL + sell_price_putS) - (buy_price_putL + buy_price_putS)

                #     trade_type = 'Put_Spread_SELLRU'
                #     # print(date,index_,trade_type,"Upper band limit exceed :",upper_band1,"Fututres Price :", current_future_price,"put spread back at : S", buy_price_putS , " and L : ", sell_price_putL)
                #     # transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,put_file_name[:-8],buy_price_put,0,put_qty,0,profit,trade_type])
                    # transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],0,0,call_file_nameS[:-8],0,0,put_file_nameL[:-8],0,0,put_file_nameS[:-8],0,0,sell_price_callL,buy_price_callS,sell_price_putL,buy_price_putS,profitC,profitP,trade_type])
                #     put_qtyL = 0
                #     put_qtyS = 0
                #     call_qtyS = 0
                #     call_qtyL = 0
                    
                if ((call_qtyL !=0) & (put_qtyL !=0)):
                    sell_price_putL = time_tempL["Put_BuyPrice"].loc[index_]
                    sell_price_callL = time_tempL["Call_BuyPrice"].loc[index_]
                    put_qtyL = -1*put_qtyL
                    call_qtyL = -1*call_qtyL
                    if spread_variant == 1:
                        buy_price_callS = time_tempS["Call_SellPrice"].loc[index_]
                        call_qtyS = -1*call_qtyS
                        buy_price_putS = time_tempS["Put_SellPrice"].loc[index_]
                        put_qtyS = -1*put_qtyS
                    else:
                        buy_price_callS = np.nan
                        buy_price_putS = np.nan
                        put_qtyS = np.nan
                        call_qtyS = np.nan
                        
                    total_transactions+=1
                    profitC = (sell_price_callL + sell_price_callS) - (buy_price_callL + buy_price_callS)
                    profitP = (sell_price_putL + sell_price_putS) - (buy_price_putL + buy_price_putS)
                    trade_type = 'Spread_RU'
                    # print(date,index_,trade_type,"Upper band limit exceed :",upper_band1,"Fututres Price :", current_future_price,"call spread back at : S", buy_price_callS , " and L : ", sell_price_callL)
                    # transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,call_file_name[:-8],buy_price_call,0,call_qty,0,profit,trade_type])
                    transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],0,0,call_file_nameS[:-8],0,0,put_file_nameL[:-8],0,0,put_file_nameS[:-8],0,0,sell_price_callL,buy_price_callS,sell_price_putL,buy_price_putS,profitC,profitP,trade_type])
                    put_qtyL = 0
                    put_qtyS = 0
                    call_qtyS = 0
                    call_qtyL = 0
                    
                '''I have closed my previous positions. I'll sell put of current ATM now as
                market is upward trending'''
                upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(current_future_price, dailyvix)
                otm_strikeCL = round(upper_band1 / roundoff_factor) * roundoff_factor
                call_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
                otm_strikePL = round(lower_band2 / roundoff_factor) * roundoff_factor
                put_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePL)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
                time_tempL = get_data(df_put_option,df_call_option)
                buy_price_callL = time_tempL["Call_SellPrice"].loc[index_]
                call_qtyL = 1
                buy_price_putL = time_tempL["Put_SellPrice"].loc[index_]
                put_qtyL = 1
                
                if spread_variant == 1:
                    otm_strikeCS = round(upper_band2 / roundoff_factor) * roundoff_factor
                    call_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
                    df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
                    otm_strikePS = round(lower_band1 / roundoff_factor) * roundoff_factor
                    put_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePS)+str("PE.NFO.csv")
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
                    time_tempS = get_data(df_put_option,df_call_option)
                    sell_price_callS = time_tempS["Call_BuyPrice"].loc[index_]
                    call_qtyS = -1
                    sell_price_putS = time_tempS["Put_BuyPrice"].loc[index_]
                    put_qtyS = -1
                else:
                    sell_price_callS = np.nan
                    sell_price_putS = np.nan
                    put_qtyS = np.nan
                    call_qtyS = np.nan
                
                trade_type = 'CS_BUY_PS_SELL_RUA'
                # trade_type = 'Put_SellRUA'
                # print(date,index_,"Rollover done Call Spread at : S: ", sell_price_callS, " L : ",buy_price_callL,"new strike price is :", call_file_nameL ,"and : ",call_file_nameS,"Futures at :", current_future_price)
                transactions_book.append([date,date_name,index_,current_future_price,current_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],buy_price_callL,call_qtyL,call_file_nameS[:-8],sell_price_callS,call_qtyS,put_file_nameL[:-8],buy_price_putL,put_qtyL,put_file_nameS[:-8],sell_price_putS,put_qtyS,0,0,0,0,0,0,trade_type])
                total_transactions+=1
                ref_future_price = current_future_price
                # print(date,index_,trade_type,"range after rollover with upper band :",upper_band1, lower_band1,"Future at :",future_price)

            # elif(time_temp['Futures_Price'].loc[index_] < lower_band):
            elif(current_future_price < lower_band1):
                # print("Check Lower band")
                # if (put_qtyL !=0) :    
                #     sell_price_putL = time_tempL["Put_BuyPrice"].loc[index_]
                #     sell_price_callL = time_tempL["Call_BuyPrice"].loc[index_]
                #     put_qtyL = -1*put_qtyL
                #     call_qtyL = -1*call_qtyL
                #     if spread_variant == 1:
                #         buy_price_callS = time_tempS["Call_SellPrice"].loc[index_]
                #         call_qtyS = -1*call_qtyS
                #         buy_price_putS = time_tempS["Put_SellPrice"].loc[index_]
                #         put_qtyS = -1*put_qtyS
                #     else:
                #         buy_price_callS = np.nan
                #         buy_price_putS = np.nan
                #         put_qtyS = np.nan
                #         call_qtyS = np.nan
                    
                #     # put_qtyS = -1*put_qtyS
                #     total_transactions+=1
                #     profitC = (sell_price_callL + sell_price_callS) - (buy_price_callL + buy_price_callS)
                #     profitP = (sell_price_putL + sell_price_putS) - (buy_price_putL + buy_price_putS)
                #     trade_type = 'Put_Spread_SELLRL'
                #     # print(date,index_,trade_type,"Lower band limit exceed :",lower_band1,"Fututres Price :", current_future_price,"put bought back at :", buy_price_put)
                    # transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],0,0,call_file_nameS[:-8],0,0,put_file_nameL[:-8],0,0,put_file_nameS[:-8],0,0,sell_price_callL,buy_price_callS,sell_price_putL,buy_price_putS,profitC,profitP,trade_type])
                #     put_qtyL = 0
                #     put_qtyS = 0
                #     call_qtyS = 0
                #     call_qtyL = 0
                    
                    
                if ((call_qtyL !=0) & (put_qtyL !=0)):
                    sell_price_putL = time_tempL["Put_BuyPrice"].loc[index_]
                    sell_price_callL = time_tempL["Call_BuyPrice"].loc[index_]
                    put_qtyL = -1*put_qtyL
                    call_qtyL = -1*call_qtyL
                    if spread_variant == 1:
                        buy_price_callS = time_tempS["Call_SellPrice"].loc[index_]
                        call_qtyS = -1*call_qtyS
                        buy_price_putS = time_tempS["Put_SellPrice"].loc[index_]
                        put_qtyS = -1*put_qtyS
                    else:
                        buy_price_callS = np.nan
                        buy_price_putS = np.nan
                        put_qtyS = np.nan
                        call_qtyS = np.nan
                        
                    total_transactions+=1
                    profitC = (sell_price_callL + sell_price_callS) - (buy_price_callL + buy_price_callS)
                    profitP = (sell_price_putL + sell_price_putS) - (buy_price_putL + buy_price_putS)
                    trade_type = 'Spread_RL'
                    # print(date,index_,trade_type,"Lower band limit exceed :", lower_band1,"Fututres Price :", current_future_price,"call bought back at :", buy_price_call)
                    # transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,call_file_name[:-8],buy_price_call,0,call_qty,0,profit,trade_type])
                    transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],0,0,call_file_nameS[:-8],0,0,put_file_nameL[:-8],0,0,put_file_nameS[:-8],0,0,sell_price_callL,buy_price_callS,sell_price_putL,buy_price_putS,profitC,profitP,trade_type])
                    put_qtyL = 0
                    put_qtyS = 0
                    call_qtyS = 0
                    call_qtyL = 0
                    
                '''I have closed my previous positions. I'll sell call of current ATM now as
                market is downward trending'''
                upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(current_future_price, dailyvix)
                
                # df_call_option = pd.DataFrame(columns = ['Ticker', 'Date', 'Time', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice','SellQty', 'LTQ', 'OpenInterest'])
                otm_strikePL = round(lower_band1 / roundoff_factor) * roundoff_factor
                put_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePL)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
                otm_strikeCL = round(upper_band2 / roundoff_factor) * roundoff_factor
                call_file_nameL=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
                time_tempL = get_data(df_put_option,df_call_option)
                buy_price_putL = time_tempL["Put_SellPrice"].loc[index_]
                put_qtyL = 1
                buy_price_callL = time_tempL["Call_SellPrice"].loc[index_]
                call_qtyL = 1
                
                if spread_variant == 1:
                    otm_strikeCS = round(upper_band1 / roundoff_factor) * roundoff_factor
                    call_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
                    otm_strikePS = round(lower_band2 / roundoff_factor) * roundoff_factor
                    put_file_nameS=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(otm_strikePS)+str("PE.NFO.csv")
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
                    df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
                    time_tempS = get_data(df_put_option,df_call_option)
                    sell_price_putS = time_tempS["Put_BuyPrice"].loc[index_]
                    put_qtyS = -1
                    sell_price_callS = time_tempS["Call_BuyPrice"].loc[index_]
                    call_qtyS = -1
                else:
                    sell_price_callS = np.nan
                    sell_price_putS = np.nan
                    put_qtyS = np.nan
                    call_qtyS = np.nan
                trade_type = 'CS_SELL_PS_BUY_RLA'
 
                # print(date,index_,"Rollover done Call sold at :", sell_price_call,"new strike price is :", call_file_name,"Futures at :", future_price)
                transactions_book.append([date,date_name,index_,current_future_price,current_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],buy_price_callL,call_qtyL,call_file_nameS[:-8],sell_price_callS,call_qtyS,put_file_nameL[:-8],buy_price_putL,put_qtyL,put_file_nameS[:-8],sell_price_putS,put_qtyS,0,0,0,0,0,0,trade_type])
                total_transactions+=1
                ref_future_price = current_future_price
                # print(date,index_,trade_type,"range after rollover with lower band :",upper_band1, lower_band1,"Future at :",future_price)
        
        elif((date == expiry_date) & (index_ >= end_time)):
            current_future_price = df_weekly_futures[df_weekly_futures["Time"] == index_].iloc[:,7].values[0]
            # if expiry_freq == "W":
            #     new_expiry = get_expiry_date(pd.to_datetime(expiry_date, format = "%d-%m-%Y") + timedelta(days=1), expiry_freq)
            # elif expiry_freq == "M":
            new_expiry = get_expiry_date(pd.to_datetime(expiry_date, format = "%d-%m-%Y") + timedelta(days=2), expiry_freq)

            expiry_month_name=pd.to_datetime(new_expiry, format ="%d-%m-%Y").strftime("%B")   
            # upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(ref_future_price, dailyvix)
            
            # if(put_qtyL!=0):
            #     '''Close existing put position to rollover'''
            #     sell_price_putL = time_tempL["Put_BuyPrice"].loc[index_]
            #     sell_price_callL = time_tempL["Call_BuyPrice"].loc[index_]
            #     put_qtyL = -1*put_qtyL
            #     call_qtyL = -1*call_qtyL
            #     if spread_variant == 1:
            #         buy_price_callS = time_tempS["Call_SellPrice"].loc[index_]
            #         call_qtyS = -1*call_qtyS
            #         buy_price_putS = time_tempS["Put_SellPrice"].loc[index_]
            #         put_qtyS = -1*put_qtyS
            #     else:
            #         buy_price_callS = np.nan
            #         buy_price_putS = np.nan
            #         put_qtyS = np.nan
            #         call_qtyS = np.nan
                
            #     # put_qtyS = -1*put_qtyS
            #     total_transactions+=1
            #     profitC = (sell_price_callL + sell_price_callS) - (buy_price_callL + buy_price_callS)
            #     profitP = (sell_price_putL + sell_price_putS) - (buy_price_putL + buy_price_putS)
            #     trade_type = 'Put_Spread_SELLRT'
            #     # print(date,index_,trade_type,"Upper band limit exceed :",upper_band1,"Fututres Price :", current_future_price,"put bought back at :", buy_price_put)
            #     # transactions_book.append([date,date_name,index_,current_future_price,upper_band,lower_band,put_file_name[:-8],buy_price_put,0,put_qty,0,profit,trade_type])
            #     transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],0,0,call_file_nameS[:-8],0,0,sell_price_callL,buy_price_callS,sell_price_putL,buy_price_putS,profitC,profitP,trade_type])
            #     put_qtyL = 0
            #     put_qtyS = 0
            #     call_qtyS = 0
            #     call_qtyL = 0
            #     '''Open put sell position with same strike for next expiry'''
                
            #     # upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(ref_future_price, dailyvix)
            #     otm_strikePL = round(lower_band1 / roundoff_factor) * roundoff_factor
            #     put_file_nameL=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikePL)+str("PE.NFO.csv")
            #     df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
            #     otm_strikeCL = round(upper_band2 / roundoff_factor) * roundoff_factor
            #     call_file_nameL=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
            #     df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
                
            #     time_tempL = get_data(df_put_option,df_call_option)
            #     buy_price_putL = time_tempL["Put_SellPrice"].loc[start_time]
            #     put_qtyL = 1
            #     buy_price_callL = time_tempL["Call_SellPrice"].loc[start_time]
            #     call_qtyL = 1
                
            #     if spread_variant == 1:
            #         otm_strikeCS = round(upper_band1 / roundoff_factor) * roundoff_factor
            #         call_file_nameS=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
            #         otm_strikePS = round(lower_band2 / roundoff_factor) * roundoff_factor
            #         put_file_nameS=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikePS)+str("PE.NFO.csv")
            #         df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
            #         df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
            #         time_tempS = get_data(df_put_option,df_call_option)
            #         sell_price_putS = time_tempS["Put_BuyPrice"].loc[start_time]
            #         put_qtyS = -1
            #         sell_price_callS = time_tempS["Call_BuyPrice"].loc[start_time]
            #         call_qtyS = -1
            #     else:
            #         sell_price_putS = np.nan
            #         put_qtyS = np.nan
            #         sell_price_callS = np.nan
            #         call_qtyS = np.nan
            #     trade_type = 'Put_Spread_BUYRT'
            #     # print(date,index_,"Rollover done on Thursday Put sold at :", sell_price_put,"new strike price is :", put_file_name,"Futures at :", future_price)
            #     transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],buy_price_callL,call_qtyL,call_file_nameS[:-8],sell_price_callS,call_qtyS,put_file_nameL[:-8],buy_price_putL,put_qtyL,put_file_nameS[:-8],sell_price_putS,put_qtyS,0,0,0,0,0,0,trade_type])
            #     total_transactions+=1
                # print(date,index_,trade_type,"range after rollover ",upper_band1, lower_band1,"Future at :",future_price)

            if((call_qtyL!=0) & (put_qtyL!=0)):
                '''Close existing call position to rollover'''
                sell_price_putL = time_tempL["Put_BuyPrice"].loc[index_]
                sell_price_callL = time_tempL["Call_BuyPrice"].loc[index_]
                put_qtyL = -1*put_qtyL
                call_qtyL = -1*call_qtyL
                if spread_variant == 1:
                    buy_price_callS = time_tempS["Call_SellPrice"].loc[index_]
                    call_qtyS = -1*call_qtyS
                    buy_price_putS = time_tempS["Put_SellPrice"].loc[index_]
                    put_qtyS = -1*put_qtyS
                else:
                    buy_price_callS = np.nan
                    buy_price_putS = np.nan
                    put_qtyS = np.nan
                    call_qtyS = np.nan
                    
                total_transactions+=1
                profitC = (sell_price_callL + sell_price_callS) - (buy_price_callL + buy_price_callS)
                profitP = (sell_price_putL + sell_price_putS) - (buy_price_putL + buy_price_putS)
                trade_type = 'Spread_RT'
                # print(date,index_,trade_type,call_strike,"call Rollover for next thursday Fututres Price :", current_future_price,"call rolled at :", buy_price_call)
                transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],0,0,call_file_nameS[:-8],0,0,put_file_nameL[:-8],0,0,put_file_nameS[:-8],0,0,sell_price_callL,buy_price_callS,sell_price_putL,buy_price_putS,profitC,profitP,trade_type])
                put_qtyL = 0
                put_qtyS = 0
                call_qtyS = 0
                call_qtyL = 0
                '''Open call sell position with same strike for next expiry'''
                
                # upper_band1,upper_band2, lower_band1,lower_band2 = get_bands(ref_future_price, dailyvix)
                otm_strikeCL = round(upper_band1 / roundoff_factor) * roundoff_factor
                call_file_nameL=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikeCL)+str("CE.NFO.csv")
                df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameL))
                otm_strikePL = round(lower_band2 / roundoff_factor) * roundoff_factor
                put_file_nameL=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikePL)+str("PE.NFO.csv")
                df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameL))
                time_tempL = get_data(df_put_option,df_call_option)
                buy_price_callL = time_tempL["Call_SellPrice"].loc[index_]
                call_qtyL = 1
                buy_price_putL = time_tempL["Put_SellPrice"].loc[index_]
                put_qtyL = 1
                if spread_variant == 1:
                    otm_strikeCS = round(upper_band2 / roundoff_factor) * roundoff_factor
                    call_file_nameS=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikeCS)+str("CE.NFO.csv")
                    df_call_option = pd.read_csv(zf1.open(folder_name_ + call_file_nameS))
                    otm_strikePS = round(lower_band1 / roundoff_factor) * roundoff_factor
                    put_file_nameS=instrument.upper()+new_expiry[:2]+(expiry_month_name[slice(3)]).upper()+new_expiry[8:]+str(otm_strikePS)+str("PE.NFO.csv")
                    df_put_option = pd.read_csv(zf1.open(folder_name_ + put_file_nameS))
                    
                    time_tempS = get_data(df_put_option,df_call_option)
                    sell_price_callS = time_tempS["Call_BuyPrice"].loc[index_]
                    call_qtyS = -1
                    sell_price_putS = time_tempS["Put_BuyPrice"].loc[index_]
                    put_qtyS = -1
                else:
                    sell_price_putS = np.nan
                    put_qtyS = np.nan
                    sell_price_callS = np.nan
                    call_qtyS = np.nan
                trade_type = 'Spread_RTA'
                # print(date,index_,"Rollover done Call sold  at :", sell_price_call,"new strike price is :", call_file_name,"Futures at :", future_price)
                transactions_book.append([date,date_name,index_,current_future_price,ref_future_price,vixdf.loc[date].values[0],upper_band2,upper_band1,lower_band1,lower_band2,call_file_nameL[:-8],buy_price_callL,call_qtyL,call_file_nameS[:-8],sell_price_callS,call_qtyS,put_file_nameL[:-8],buy_price_putL,put_qtyL,put_file_nameS[:-8],sell_price_putS,put_qtyS,0,0,0,0,0,0,trade_type])
                total_transactions+=1
            expiry_date = new_expiry   
             
transactions_book_df = pd.DataFrame(transactions_book[1:],   columns = transactions_book[0])
transactions_book_df.to_csv("../ShivamStrat2_Test4W.csv", index = False)