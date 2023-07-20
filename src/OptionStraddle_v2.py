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
import datetime as dt
import os
import math
import zipfile

def get_next_day(date, get_day):
    # today_ = datetime()
    date_ = pd.to_datetime(date, format = "%d-%m-%Y")
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


    
stoploss_percent = 0.16
stoploss_percent_combined = 0.01
instrument = "BANKNIFTY"

# instrument = "NIFTY"
if instrument == "BANKNIFTY":
    roundoff_factor = 100
    start_time = "09:44:00"
    end_time = "14:41:00"
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
path_for_weekly_futures=r'C:/Users/Jatin/Downloads/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path = "C:/Users/Jatin/Downloads/Compressed/"
day_profit = {}
date_list = ["02-11-2021", "02-11-2021", "03-11-2021","31-12-2021"]
# ,"02-11-2021", "02-11-2021", "03-11-2021", "08-11-2021", "09-11-2021", "10-11-2021"]

for date in date_list:
    # date = "02-11-2021"
    # date = date_list[0]
# date = "2021/01/01"
    # try:

    
    # bnifty_p = dfbnifty_price["O"][(dfbnifty_price["Date"] == date) & (dfbnifty_price["Time"] == start_time)].values[0]
    if pd.to_datetime(date, format = "%d-%m-%Y")>=pd.to_datetime( "01-02-2022", format = "%d-%m-%Y"):
        folder_name="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
        folder_name_ = "GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/Options'+'/'
    else:
        folder_name="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
        folder_name_ = "GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
    # finding the month name
    month_name=pd.to_datetime(date, format = "%d-%m-%Y").strftime("%B")
    dir_1=changing_path + date[-4:] + "/" + month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    # os.chdir(dir_1)
                
    #Now finding the file_name that needs to be opened
    to_zip=dir_1+folder_name[:-1]+str(".zip")
    
    # with ZipFile(to_zip,"r") as zip:
    #     print("Extracting Zip files... " + date)
    #     zip.extractall(dir_1)
    zf = zipfile.ZipFile(to_zip)
            
    time_temp=pd.read_csv("TimeTemplate.csv")
    
    '''read Futures file for that day. took future's price as of start_time to calculate ATM'''
    weekly_futures_filename = path_for_weekly_futures + "/" + month_name[0:3]+ "'"+date[-2:] + "/"+ pd.to_datetime(date , format = '%d-%m-%Y').strftime("%d%m%Y") + "_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    wfut_cols = [x for x in df_weekly_futures.columns if "WFUT" in x]
    future_price = df_weekly_futures[wfut_cols[0]][df_weekly_futures["Time"] == start_time].values[0]
    
    check_combined_stoploss = False
    otm_value_wed_thu = 0

    # if pd.to_datetime(date).strftime("%A") in ['Thursday', 'Wednesday']:
    #     check_combined_stoploss = True
    #     otm_value_wed_thu = 100

        
    working_strike = round(future_price / roundoff_factor) * roundoff_factor
    call_strike = working_strike + otm_value_wed_thu
    put_strike = working_strike - otm_value_wed_thu
    
    df_weekly_futures_used = df_weekly_futures[['Time' ,wfut_cols[0] ]].copy()
    data_futures=df_weekly_futures_used.drop_duplicates(["Time"])
    # data_futures=pd.merge(data_futures,time_temp,how="right",right_on="Time",left_on="Time")
    data_futures=data_futures.fillna(method="bfill")
    # data_futures=data_futures.fillna(method="ffill")
    time_temp[wfut_cols[0]] = data_futures[wfut_cols[0]]
    time_temp.set_index("Time", inplace = True)
        
    '''Get expiry date and then get file for both and call option for their respective Strike price'''
    expiry_date = get_expiry_date(date)    
    expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
    put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
    call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
    
    # df_call_option = pd.read_csv(dir_1+folder_name + call_file_name, header = 0)
    # df_put_option = pd.read_csv(dir_1+folder_name + put_file_name, header = 0)
    df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
    data_put_atm=df_put_option.drop_duplicates(["Time"])
    data_put_atm.set_index("Time", inplace = True)
    time_temp[put_file_name[:-8]+"_LTP"] = data_put_atm["LTP"]
    time_temp[put_file_name[:-8]+"_BuyPrice"] = data_put_atm["BuyPrice"]
    time_temp[put_file_name[:-8]+"_SellPrice"] = data_put_atm["SellPrice"]
    

    data_call_atm=df_call_option.drop_duplicates(["Time"])
    data_call_atm.set_index("Time", inplace = True)
    time_temp[call_file_name[:-8]+"_LTP"] = data_call_atm["LTP"]
    time_temp[call_file_name[:-8]+"_BuyPrice"] = data_call_atm["BuyPrice"]
    time_temp[call_file_name[:-8]+"_SellPrice"] = data_call_atm["SellPrice"]
    time_temp=time_temp.fillna(method="bfill")
        
    '''Sell options at start time'''
    sell_price_put = time_temp[put_file_name[:-8]+"_BuyPrice"].loc[start_time]
    sell_price_call = time_temp[call_file_name[:-8]+"_BuyPrice"].loc[start_time]
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
    sq_off_type_C = ''
    sq_off_type_P = ''
    # trade_active = True
    # print(len(df_rel_call_option), len(df_rel_put_option))
    print(call_file_name[:-8] ," Call Sold : ", sell_price_call, put_file_name[:-8], " Put Sold : ", sell_price_put, " at Time : ", start_time)
    
    time_temp["Call_plus_Put"] = time_temp[put_file_name[:-8]+"_SellPrice"] + time_temp[call_file_name[:-8]+"_SellPrice"]
    
    for index_,row in time_temp[time_temp.index >= start_time].iterrows():
        # if (index_ == end_time):
            # print(index_ == end_time)
            # break
        # print(index,row)
        # if(check_combined_stoploss == True):
        if ((position_active_call == False) & (position_active_put == False)):
            break
        
        if((position_active_call == True) & (position_active_put == True) & (check_combined_stoploss == True)):
            curr_combined_prem = time_temp["Call_plus_Put"][index_]
            # curr_combined_prem = time_temp["Call_plus_Put"][index_] - buy_call_price - buy_put_price
            if(curr_combined_prem - combined_premium >= max_loss):
                # if(position_active_call == True):
                idx_c = np.searchsorted(time_temp.index, index_)
                index_c  = index_
                idx_p = np.searchsorted(time_temp.index, index_)
                index_p  = index_
                
                buy_call_price = time_temp[call_file_name[:-8]+"_SellPrice"][min(idx_c+1, len(time_temp)-1)]
                position_active_call = False
                # if(position_active_put == True):
                buy_put_price = time_temp[put_file_name[:-8]+"_SellPrice"][min(idx_p+1, len(time_temp)-1)]                
                position_active_put = False
                
                # max_loss =  max_loss + initial_investment*0.01 + (sell_price_call-buy_call_price)
                sq_off_type_C = 'CombinedSL_CP'
                sq_off_type_P = 'CombinedSL_CP'
                print("Combined Stop loss hit for both options buying at : ",index_)
                break
            
        if(position_active_call == True):
            # print("Check Call Position")
            if(time_temp[call_file_name[:-8]+"_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_call):
                index_c  = index_
                idx_c = np.searchsorted(time_temp.index, index_)
                buy_call_price = time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)]
                # buy_put_price = df_rel_put_option["C"][df_rel_put_option["C"]["Time"] == df_rel_call_option["Time"][i]]
                position_active_call = False
                max_loss =  max_loss + (sell_price_call-buy_call_price)
                print("Stop loss hit for call bought call option buying at : ",time_temp.index[min(idx_c+1, len(time_temp)-1)], " for : ",buy_call_price , " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'Stoploss_C'
                # continue
            
            elif((check_combined_stoploss == True) & ((sell_price_call - time_temp[call_file_name[:-8]+"_SellPrice"][index_]) <= -1*max_loss) & (position_active_put == False)):
                index_c  = index_
                idx_c = np.searchsorted(time_temp.index, index_)
                buy_call_price = time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)]
                position_active_call = False
                print("combine Stop loss hit for call option buying at : ",time_temp.index[min(idx_c+1, len(time_temp)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'CombinedSL_C'
                # continue
            
            elif(index_ == end_time):
                index_c  = index_
                idx_c = np.searchsorted(time_temp.index, index_)
                buy_call_price = time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)]
                position_active_call = False
                print("Time Close hit for call option buying at : ",time_temp.index[min(idx_c+1, len(time_temp)-1)], " for : ",buy_call_price, " making profit of : ", (sell_price_call-buy_call_price))
                sq_off_type_C = 'EndTime_C'
                # continue
        
        if(position_active_put == True):
            # print("Check Put Position : ",position_active_put,index_)
            # if (index_ == end_time):
            #     print(index_ == end_time)
            #     break
            # i
            if(time_temp[put_file_name[:-8]+"_SellPrice"][index_] >= (1+stoploss_percent)*sell_price_put):
                index_p  = index_
                idx_p = np.searchsorted(time_temp.index, index_)
                buy_put_price = time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)]
                position_active_put = False
                max_loss =  max_loss + (sell_price_put-buy_put_price)
                print("Stop loss hit for put bought put option buying at : ",time_temp.index[min(idx_p+1, len(time_temp)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price) )            
                sq_off_type_P = 'Stoploss_P'
                # continue
            
            elif((check_combined_stoploss == True) & ((sell_price_put - time_temp[put_file_name[:-8]+"_SellPrice"][index_]) <= -1*max_loss) & (position_active_call == False)):
                index_p  = index_
                idx_p = np.searchsorted(time_temp.index, index_)
                buy_put_price = time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)]
                position_active_put = False
                print("combine Stop loss hit for put option buying at : ",time_temp.index[min(idx_p+1, len(time_temp)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price))
                sq_off_type_P = 'CombinedSL_P'
                # continue
            
            elif(index_ == end_time):
                index_p  = index_
                idx_p = np.searchsorted(time_temp.index, index_)
                buy_put_price = time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)]
                position_active_put = False
                print("Time close hit for put option buying at : ",time_temp.index[min(idx_p+1, len(time_temp)-1)], " for : ",buy_put_price , " making profit of : ", (sell_price_put-buy_put_price))
                sq_off_type_P = 'EndTime_P'
                # print(index_ , end_time, "2")
                # continue
            # print(index_ , end_time)
                
            # print(buy_call_price,buy_put_price, " Last_value Put ")
    
    time_temp.to_csv('../res/' +date+"_"+str(working_strike) + '.csv' )
    
    day_profit[date] = {
     "day" : pd.to_datetime(date, format = "%d-%m-%Y").strftime("%A"),
     "Future" : future_price,
     "ATM Strike" : working_strike,
     "Sum_Premium_LTP" : (time_temp[call_file_name[:-8]+"_LTP"].loc[start_time] + time_temp[put_file_name[:-8]+"_LTP"].loc[start_time] ), 
     "Time_start"	: start_time,
     "Strike to Sell" : working_strike,	
     "Future at Sell" :future_price,
     "Call_Sell" : sell_price_call,
     "Put_Sell" : sell_price_put,	
     "Sum_Sell" : (sell_price_put +sell_price_call),
     
     # "Time_SQOFF_Call" : index_c,	
     # "Future_CALLSQOFF"	: time_temp[wfut_cols[0]][index_c],
     # "Call Buy"	: buy_call_price,
     # "Call PNL"	: (sell_price_call-buy_call_price),
     
     # "Time_SQOFF_Put"	: index_p,	
     # "Future_PUTSQOFF"	: time_temp[wfut_cols[0]][index_p],
     # "Put Buy"	: buy_put_price,
     # "Put PNL"  : (sell_price_put-buy_put_price),
      "Time_SQOFF_Call" : time_temp.index[min(idx_c+1, len(time_temp)-1)],	
      "Future_CALLSQOFF"	: time_temp[wfut_cols[0]].iloc[min(idx_c+1, len(time_temp)-1)],
      "Call Buy"	: time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)],
      "Call PNL"	: (sell_price_call - time_temp[call_file_name[:-8]+"_SellPrice"].iloc[min(idx_c+1, len(time_temp)-1)]),
     
      "Time_SQOFF_Put"	: time_temp.index[min(idx_p+1, len(time_temp)-1)],	
      "Future_PUTSQOFF"	: time_temp[wfut_cols[0]].iloc[min(idx_p+1, len(time_temp)-1)],
      "Put Buy"	: time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)],
      "Put PNL"  : (sell_price_put-time_temp[put_file_name[:-8]+"_SellPrice"].iloc[min(idx_p+1, len(time_temp)-1)]),
     
     "Time_End"	    : end_time,
     "Future at end": time_temp[wfut_cols[0]][end_time],
     "Call_end"	    : time_temp[call_file_name[:-8]+"_SellPrice"].loc[end_time],
     "Put_end"	    : time_temp[put_file_name[:-8]+"_SellPrice"].loc[end_time],
     "Sum_end"      : (time_temp[call_file_name[:-8]+"_SellPrice"].loc[end_time] + time_temp[put_file_name[:-8]+"_BuyPrice"].loc[end_time] ),
     
     "Time_Max"	    : time_temp["Call_plus_Put"].idxmax(),
     "Future_Max"	: time_temp[wfut_cols[0]][time_temp["Call_plus_Put"].idxmax()],
     "Call at Max"	: time_temp[call_file_name[:-8]+"_SellPrice"].loc[time_temp["Call_plus_Put"].idxmax()],
     "Put at Max"	: time_temp[put_file_name[:-8]+"_SellPrice"].loc[time_temp["Call_plus_Put"].idxmax()],
     "Sum_Max"      : time_temp["Call_plus_Put"].max(),
     
     "Time_Min"	    : time_temp["Call_plus_Put"].idxmin(),
     "Future_Min"	: time_temp[wfut_cols[0]][time_temp["Call_plus_Put"].idxmin()],
     "Call at Min"	: time_temp[call_file_name[:-8]+"_SellPrice"].loc[time_temp["Call_plus_Put"].idxmin()],
     "Put at Min"	: time_temp[put_file_name[:-8]+"_SellPrice"].loc[time_temp["Call_plus_Put"].idxmin()],
     "Sum_Min"      : time_temp["Call_plus_Put"].min(),
     'Close_Type_Call' : sq_off_type_C,
     'Close_Type_Put' : sq_off_type_P
         }
    
    # day_profit[date] = {"Month" : today.strftime("%B"), "Day" : str(today_day), "Sell_call" : sell_price_call,"Buy_call" : buy_call_price, "Sell_put" : sell_price_put, "Buy_Put" : buy_put_price, "CP" : sell_price_call - buy_call_price, "PP" : sell_price_put - buy_put_price}
    # except:
    #     print(date)

day_profit_df = pd.DataFrame(day_profit).T
day_profit_df.to_csv("../res/Output.csv")
# day_profit_df["Total_Profit"] = day_profit_df["CP"] + day_profit_df["PP"]

# day_profit_df["Max_Profit"] = day_profit_df["Sell_call"] + day_profit_df["Sell_put"]
# day_profit_df["Max_Profit"].sum()
# day_profit_df["Total_Profit"].sum()
# day_profit_df["Total_Profit"].mean()
# day_profit_df["Total_Profit"].std()
# day_profit_df_byday = day_profit_df.groupby("Day").sum()

# plt.figure(figsize = (16,12))
# plt.bar(day_profit_df.index, day_profit_df["Total_Profit"], color ='maroon',width = 0.4)
# plt.xticks(rotation = 90)
# plt.xlabel("Date")
# plt.ylabel("Profit")
# # plt.plot(day_profit_df["PP"])
# plt.grid()
# plt.show()

# plt.figure()
# plt.plot(range(len(time_temp.index)), time_temp["BANKNIFTY03NOV2139800PE_SellPrice"])
# plt.plot(np.searchsorted(time_temp.index, start_time),time_temp["BANKNIFTY03NOV2139800PE_BuyPrice"][start_time],'ro')
# plt.xticks(rotation = 90)
# plt.show()