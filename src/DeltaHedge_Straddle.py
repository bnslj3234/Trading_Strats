# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 18:34:34 2022

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

def cal_call_put_straddle_qty(call_D, put_D, call_qty, put_qty,initial_delta):
    if initial_delta == True:
        call_D=abs(call_D); put_D=abs(put_D)
        previous_call_qty=call_qty; previous_put_qty=put_qty
        if put_D<call_D:
            if call_qty==0:call_qty=minimum_trade_qty
            put_qty = round((call_D*call_qty/put_D)/lot_size)*lot_size
            if put_qty<=maximum_trade_qty and put_qty>=previous_put_qty: return call_qty, put_qty
            if put_qty>maximum_trade_qty:
                call_qty=round((put_D*maximum_trade_qty/call_D)/lot_size)*lot_size
                return call_qty, maximum_trade_qty
            if put_qty<previous_put_qty:
                call_qty=round((put_D*previous_put_qty/call_D)/lot_size)*lot_size
                return call_qty, previous_put_qty
        if put_D>call_D:
            if put_qty==0:put_qty=minimum_trade_qty
            call_qty = round((put_D*put_qty/call_D)/lot_size)*lot_size
            if call_qty<=maximum_trade_qty and call_qty>=previous_call_qty: return call_qty, put_qty
            if call_qty>maximum_trade_qty:
                put_qty=round((call_D*maximum_trade_qty/put_D)/lot_size)*lot_size
                return maximum_trade_qty, put_qty
            if call_qty<previous_call_qty:
                put_qty=round((call_D*previous_call_qty/put_D)/lot_size)*lot_size
                return previous_call_qty, put_qty
    elif initial_delta == False:
        call_qty=minimum_trade_qty
        put_qty=minimum_trade_qty
        return call_qty,put_qty

def change_qty_trade(new_qty,old_qty):
    if new_qty==old_qty:return 'BUY',0
    if new_qty>old_qty:return 'SELL',new_qty-old_qty
    if new_qty<old_qty:return 'BUY',old_qty-new_qty
    
day_wise_input = {'Monday' : {'stoploss_fraction' : 0.99,'stoploss_fraction_combined' : 0.99,'instrument' : "BANKNIFTY",
                              'delta_move_fraction' : 0.05,'roll_strike_fraction' : 0.0075,'index_total_move' : 220,
                              'minimum_trade_qty' : 400 ,'maximum_trade_qty' : 600,'lot_size' : 25,'call_qty_delta_neutral_perc' : 1,
                              'put_qty_delta_neutral_perc' : 0.5,'roundoff_factor' : 100,'start_time' : "09:44:00",
                              'end_time' : "14:41:00",'roundoff_factor' : 100,'check_combined_stoploss' : False,
                              'otm_value_wed_thu' : 0,'strike_change_rollover' : True,'delta_neutral_rollover' : True,
                              'check_normal_stoploss' : True},
                  
                  'Tuesday' : {'stoploss_fraction' : 0.99,'stoploss_fraction_combined' : 0.99,'instrument' : "BANKNIFTY",
                              'delta_move_fraction' : 0.05,'roll_strike_fraction' : 0.0075,'index_total_move' : 220,
                              'minimum_trade_qty' : 400 ,'maximum_trade_qty' : 600,'lot_size' : 25,'call_qty_delta_neutral_perc' : 1,
                              'put_qty_delta_neutral_perc' : 0.5,'roundoff_factor' : 100,'start_time' : "09:44:00",
                              'end_time' : "14:41:00",'roundoff_factor' : 100,'check_combined_stoploss' : False,
                              'otm_value_wed_thu' : 0,'strike_change_rollover' : True,'delta_neutral_rollover' : True,
                              'check_normal_stoploss' : True},
                  
                  'Wednesday' : {'stoploss_fraction' : 0.99,'stoploss_fraction_combined' : 0.99,'instrument' : "BANKNIFTY",
                              'delta_move_fraction' : 0.05,'roll_strike_fraction' : 0.0075,'index_total_move' : 220,
                              'minimum_trade_qty' : 400 ,'maximum_trade_qty' : 600,'lot_size' : 25,'call_qty_delta_neutral_perc' : 1,
                              'put_qty_delta_neutral_perc' : 0.5,'roundoff_factor' : 100,'start_time' : "09:44:00",
                              'end_time' : "14:41:00",'roundoff_factor' : 100,'check_combined_stoploss' : False,
                              'otm_value_wed_thu' : 0,'strike_change_rollover' : True,'delta_neutral_rollover' : True,
                              'check_normal_stoploss' : True},
                  
                  'Thursday' : {'stoploss_fraction' : 0.99,'stoploss_fraction_combined' : 0.99,'instrument' : "BANKNIFTY",
                              'delta_move_fraction' : 0.05,'roll_strike_fraction' : 0.0075,'index_total_move' : 220,
                              'minimum_trade_qty' : 400 ,'maximum_trade_qty' : 600,'lot_size' : 25,'call_qty_delta_neutral_perc' : 1,
                              'put_qty_delta_neutral_perc' : 0.5,'roundoff_factor' : 100,'start_time' : "09:44:00",
                              'end_time' : "14:41:00",'roundoff_factor' : 100,'check_combined_stoploss' : False,
                              'otm_value_wed_thu' : 0,'strike_change_rollover' : True,'delta_neutral_rollover' : True,
                              'check_normal_stoploss' : True},
                  
                  'Friday' : {'stoploss_fraction' : 0.99,'stoploss_fraction_combined' : 0.99,'instrument' : "BANKNIFTY",
                              'delta_move_fraction' : 0.05,'roll_strike_fraction' : 0.0075,'index_total_move' : 220,
                              'minimum_trade_qty' : 400 ,'maximum_trade_qty' : 600,'lot_size' : 25,'call_qty_delta_neutral_perc' : 1,
                              'put_qty_delta_neutral_perc' : 0.5,'roundoff_factor' : 100,'start_time' : "09:44:00",
                              'end_time' : "14:41:00",'roundoff_factor' : 100,'check_combined_stoploss' : False,
                              'otm_value_wed_thu' : 0,'strike_change_rollover' : True,'delta_neutral_rollover' : True,
                              'check_normal_stoploss' : True}
                  }

trade_type_C = ''
trade_type_P = ''
float_nan = np.nan

date_list = pd.read_csv("Backtest_Dates.csv", header = 0)["Date"].dropna().tolist()
holidays_list = pd.read_csv("HolidayList.csv")
Thur_Hols = holidays_list["Date"][holidays_list["Day"] == "Thursday"].tolist()
Wed_hol = holidays_list["Date"][holidays_list["Day"] == "Wednesday"].tolist()
# path_for_weekly_futures=r'D:/Options/BankNifty Output'
path_for_weekly_futures=r'C:/Users/Jatin/Downloads/'
# changing_path = r'D:/Options/GDFL Raw Data/'
changing_path = "C:/Users/Jatin/Downloads/Compressed/"
# day_profit = {}
transactions_book = [["Date", 'Day',"Time","FuturesPrice",'Delta_Upper_Band','Delta_Lower_Band','Strike_Change_Band','Strike_Change_Lower_Band',
    'Call_Instrument_Name', 'CallBuyPrice', 'CallBuyQty', 'CallSellPrice','CallSellQty',"CallProfit","Calltrade_type",
    'Put_Instrument_Name', 'PutBuyPrice', 'PutBuyQty', 'PutSellPrice','PutSellQty',"PutProfit","Puttrade_type"]]
date_list = ["02-11-2021", "03-11-2021", "08-11-2021", "09-11-2021", "10-11-2021", "11-11-2021"]
# ,"08-11-2021","09-11-2021"]
# ,"02-11-2021", "02-11-2021", "03-11-2021", "08-11-2021", "09-11-2021", "10-11-2021"]


for date in date_list:
    # date = "02-11-2021"
    # date = date_list[0]
# date = "2021/01/01"
    # try:
    month_name=pd.to_datetime(date, format = "%d-%m-%Y").strftime("%B")
    dir_1=changing_path + date[-4:] + "/" + month_name[0:3].upper()+"_"+str(date[-4:]) + '/'
    date_name = pd.to_datetime(date, format ="%d-%m-%Y").strftime("%A")
    
    stoploss_fraction = day_wise_input[date_name]['stoploss_fraction']
    stoploss_fraction_combined = day_wise_input[date_name]['stoploss_fraction_combined']
    instrument = day_wise_input[date_name]['instrument']
    delta_move_fraction = day_wise_input[date_name]['delta_move_fraction']
    roll_strike_fraction = day_wise_input[date_name]['roll_strike_fraction']
    index_total_move= day_wise_input[date_name]['index_total_move']
    minimum_trade_qty = day_wise_input[date_name]['minimum_trade_qty']
    maximum_trade_qty = day_wise_input[date_name]['maximum_trade_qty']
    lot_size = day_wise_input[date_name]['lot_size']
    call_qty_delta_neutral_perc = day_wise_input[date_name]['call_qty_delta_neutral_perc']
    put_qty_delta_neutral_perc = day_wise_input[date_name]['put_qty_delta_neutral_perc']
    roundoff_factor = day_wise_input[date_name]['roundoff_factor']
    start_time = day_wise_input[date_name]['start_time']
    end_time = day_wise_input[date_name]['end_time']
    roundoff_factor = day_wise_input[date_name]['roundoff_factor']
    check_combined_stoploss = day_wise_input[date_name]['check_combined_stoploss']
    otm_value_wed_thu = day_wise_input[date_name]['otm_value_wed_thu']
    strike_change_rollover = day_wise_input[date_name]['strike_change_rollover']
    delta_neutral_rollover = day_wise_input[date_name]['delta_neutral_rollover']
    check_normal_stoploss = day_wise_input[date_name]['check_normal_stoploss']
    if pd.to_datetime(date, format = "%d-%m-%Y")>=pd.to_datetime( "01-02-2022", format = "%d-%m-%Y"):
        folder_name="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
        folder_name_ = "GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/Options'+'/'
    else:
        folder_name="GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
        folder_name_ = "GFDLNFO_TICK_"+date[:2]+date[3:5]+date[-4:]+'/'
                    
    #Now finding the file_name that needs to be opened
    to_zip=dir_1+folder_name[:-1]+str(".zip")
    zf = zipfile.ZipFile(to_zip)
                
    '''read Futures file for that day. took future's price as of start_time to calculate ATM'''
    weekly_futures_filename = path_for_weekly_futures + "/" + month_name[0:3]+ "'"+date[-2:] + "/"+ pd.to_datetime(date , format = '%d-%m-%Y').strftime("%d%m%Y") + "_results.csv"
    df_weekly_futures = pd.read_csv(weekly_futures_filename, index_col=('Unnamed: 0'))
    wfut_cols = [x for x in df_weekly_futures.columns if "WFUT" in x]
    future_price = df_weekly_futures[wfut_cols[0]][df_weekly_futures["Time"] == start_time].values[0]
    
    # check_combined_stoploss = False
    # otm_value_wed_thu = 0
    # strike_change_rollover = True
    # delta_neutral_rollover = True

    # if pd.to_datetime(date).strftime("%A") in ['Thursday', 'Wednesday']:
    #     check_combined_stoploss = True
    #     otm_value_wed_thu = 100

        
    working_strike = round(future_price / roundoff_factor) * roundoff_factor
    call_strike = working_strike + otm_value_wed_thu
    put_strike = working_strike - otm_value_wed_thu
    
    working_strike_info = ["Time"] + [x for x in df_weekly_futures.columns if str(working_strike) in x]
    # df_weekly_futures_used = df_weekly_futures[working_strike_info].copy(
    df_weekly_futures_used = df_weekly_futures.copy()
    df_weekly_futures_used.set_index("Time", inplace = True)
    # data_futures=df_weekly_futures_used.drop_duplicates(["Time"])
    # data_futures=data_futures.fillna(method="bfill")
    # # data_futures=data_futures.fillna(method="ffill")
    # time_temp[[str(working_strike)+'WFUT']] = data_futures[[str(working_strike)+'WFUT']]
    # time_temp.set_index("Time", inplace = True)
        
    '''Get expiry date and then get file for both and call option for their respective Strike price'''
    expiry_date = get_expiry_date(date)    
    expiry_month_name=pd.to_datetime(expiry_date, format = "%d-%m-%Y").strftime("%B")
    put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(put_strike)+str("PE.NFO.csv")
    call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(call_strike)+str("CE.NFO.csv")
    
    # df_call_option = pd.read_csv(dir_1+folder_name + call_file_name, header = 0)
    # df_put_option = pd.read_csv(dir_1+folder_name + put_file_name, header = 0)
    # df_put_option = pd.read_csv(zf.open(folder_name_ + put_file_name))
    # df_call_option = pd.read_csv(zf.open(folder_name_+call_file_name))
    
    # data_put_atm=df_put_option.drop_duplicates(["Time"])
    # data_put_atm.set_index("Time", inplace = True)
    # time_temp[put_file_name[:-8]+"_LTP"] = data_put_atm["LTP"]
    # time_temp[put_file_name[:-8]+"_BuyPrice"] = data_put_atm["BuyPrice"]
    # df_weekly_futures_used[str(working_strike) + "P_S"] = data_put_atm["SellPrice"]
    

    # data_call_atm=df_call_option.drop_duplicates(["Time"])
    # data_call_atm.set_index("Time", inplace = True)
    # time_temp[call_file_name[:-8]+"_LTP"] = data_call_atm["LTP"]
    # time_temp[call_file_name[:-8]+"_BuyPrice"] = data_call_atm["BuyPrice"]
    # df_weekly_futures_used[str(working_strike) + "C_S"] = data_call_atm["SellPrice"]
    # time_temp=time_temp.fillna(method="bfill")
    # str(working_strike) + "P_B"
    fut_price = df_weekly_futures_used[str(working_strike)+'WFUT'].loc[start_time]
    delta_move_lower_price=fut_price*(1-delta_move_fraction)    
    delta_move_upper_price=fut_price*(1+delta_move_fraction)
    strike_move_lower_price=fut_price*(1-roll_strike_fraction)    
    strike_move_upper_price=fut_price*(1+roll_strike_fraction)
    
    '''Sell options at start time'''
    # "Date", 'Day',"Time","FuturesPrice",'Delta_Upper_Band','Delta_Lower_Band','Strike_Change_Band','Strike_Change_Lower_Band',
    # 'CallInstrument_Name', 'CallBuyPrice', 'CallBuyQty', 'CallSellPrice','CallSellQty',"CallProfit","Calltrade_type",
    # 'PutInstrument_Name', 'PutBuyPrice', 'PutBuyQty', 'PutSellPrice','PutSellQty',"PutProfit","Puttrade_type"
    sell_price_put = df_weekly_futures_used[str(working_strike) + "P_B"].loc[start_time]
    sell_price_call = df_weekly_futures_used[str(working_strike) + "C_B"].loc[start_time]
    trade_type_C = "Call_Sell1"
    trade_type_P = "Put_Sell1"
    position_active_call = True
    position_active_put = True
    buy_price_put = 0
    buy_price_call = 0
    call_qty = -1*minimum_trade_qty
    put_qty = -1*minimum_trade_qty
    # cal_call_put_straddle_qty()
    call_D = df_weekly_futures_used[str(working_strike) + "C_Delta"].loc[start_time]
    put_D = df_weekly_futures_used[str(working_strike) + "P_Delta"].loc[start_time]
    call_qty,put_qty = cal_call_put_straddle_qty(call_D, put_D, 0, 0,delta_neutral_rollover)
    call_qty = -1*call_qty
    put_qty = -1*put_qty
    transactions_book.append([date,date_name,start_time,fut_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],0,0,sell_price_call,call_qty,0,trade_type_C,
                             put_file_name[:-8],0,0,sell_price_put,put_qty,0,trade_type_P])
    combined_premium = sell_price_put + sell_price_call
    initial_investment = (working_strike)*0.2*2
    max_loss = int(180000*stoploss_fraction_combined/25)
    
    # new range for wednesday and thursday
    # strike_move_lower_price = max(strike_move_lower_price, fut_price - min((combined_premium)* stoploss_fraction_combined, index_total_move))
    # strike_move_upper_price = min(strike_move_upper_price, fut_price + min((combined_premium)* stoploss_fraction_combined, index_total_move))
    

    # buy_call_time = 0
    # buy_put_time = 0

    # trade_active = True
    # print(len(df_rel_call_option), len(df_rel_put_option))
    print(date,start_time,call_file_name[:-8] ," Call Sold : ", sell_price_call, put_file_name[:-8], " Put Sold : ", sell_price_put, " at Time : ", start_time)
    
    df_weekly_futures_used["Call_plus_Put"] = df_weekly_futures_used[str(working_strike) + "P_B"] + df_weekly_futures_used[str(working_strike) + "C_B"]
    
    for index_,row in df_weekly_futures_used[df_weekly_futures_used.index >= start_time].iterrows():
        call_IV = df_weekly_futures_used[str(working_strike) + "_IV"].loc[index_]
        put_IV = df_weekly_futures_used[str(working_strike) + "_IV"].loc[index_]
        
        call_D = df_weekly_futures_used[str(working_strike) + "C_Delta"].loc[index_]
        put_D = df_weekly_futures_used[str(working_strike) + "P_Delta"].loc[index_]
        current_future_price = df_weekly_futures_used[str(working_strike)+'WFUT'].loc[index_]
        if np.isnan(call_IV) or np.isnan(put_IV) or np.isnan(call_D) or np.isnan(put_D):
            print(date,index_,' Call Put IV & Delta Issue :: ',call_IV,put_IV,call_D,put_D)
            continue
        
        if ((position_active_call == False) & (position_active_put == False)):
            break
        
        if((position_active_call == True) & (position_active_put == True) & (check_combined_stoploss == True)):
            curr_combined_prem = df_weekly_futures_used["Call_plus_Put"][index_]
            # curr_combined_prem = time_temp["Call_plus_Put"][index_] - buy_price_call - buy_price_put
            if(curr_combined_prem - combined_premium >= max_loss):
                # if(position_active_call == True):
                idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                index_c  = index_
                idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                index_p  = index_
                
                buy_price_call = df_weekly_futures_used[str(working_strike) + "C_S"][min(idx_c+1, len(df_weekly_futures_used)-1)]
                call_qty = -1*call_qty
                position_active_call = False
                # if(position_active_put == True):
                buy_price_put = df_weekly_futures_used[str(working_strike) + "P_S"][min(idx_p+1, len(df_weekly_futures_used)-1)]                
                position_active_put = False
                put_qty = -1*put_qty
                
                # max_loss =  max_loss + initial_investment*0.01 + (sell_price_call-buy_price_call)
                trade_type_C = 'BUY_CombinedSL_CP'
                trade_type_P = 'BUY_CombinedSL_CP'
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],buy_price_call,call_qty,0,0,sell_price_call - buy_price_call,trade_type_C,
                             put_file_name[:-8],buy_price_put,put_qty,0, 0,sell_price_put-buy_price_put,trade_type_P])
                put_qty = 0
                call_qty = 0
                print(date,index_,"Combined Stop loss hit for both options buying at : ",index_)
                break
            
        if((position_active_call == True) & (position_active_put == True) & (strike_change_rollover == True)):
            if((current_future_price<=strike_move_lower_price) | (current_future_price>=strike_move_upper_price)):
                qty_for_next_cycle = max(minimum_trade_qty, min(-1*call_qty,-1*put_qty))
                idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                index_c  = index_
                idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                index_p  = index_
                
                buy_price_call = df_weekly_futures_used[str(working_strike) + "C_S"][min(idx_c+1, len(df_weekly_futures_used)-1)]
                call_qty = -1*call_qty
                # position_active_call = False
                # if(position_active_put == True):
                buy_price_put = df_weekly_futures_used[str(working_strike) + "P_S"][min(idx_p+1, len(df_weekly_futures_used)-1)]                
                # position_active_put = False
                put_qty = -1*put_qty
                trade_type_C = 'BUY_StrikeChange_CP'
                trade_type_P = 'BUY_StrikeChange_CP'
                print(buy_price_call,buy_price_put)
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],buy_price_call,call_qty,0,0,sell_price_call - buy_price_call,trade_type_C,
                             put_file_name[:-8],buy_price_put,put_qty,0, 0,sell_price_put-buy_price_put,trade_type_P])
                print(date,index_,"Strike change squareoff hit for both options buying at : ",index_, "call_qty :", call_qty, "put_qty :", put_qty)
                put_qty = 0
                call_qty = 0
                print(date,index_,"Strike change squareoff hit for both options Selling start at : ",index_, "current call_qty :", call_qty, "put_qty :", put_qty)
                new_working_strike = round(current_future_price / roundoff_factor) * roundoff_factor
                put_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(new_working_strike)+str("PE.NFO.csv")
                call_file_name=instrument.upper()+expiry_date[:2]+(expiry_month_name[slice(3)]).upper()+expiry_date[8:]+str(new_working_strike)+str("CE.NFO.csv")
                '''Reset delta and strike  change range'''
                delta_move_lower_price=current_future_price*(1-delta_move_fraction)    
                delta_move_upper_price=current_future_price*(1+delta_move_fraction)
                strike_move_lower_price=current_future_price*(1-roll_strike_fraction)    
                strike_move_upper_price=current_future_price*(1+roll_strike_fraction)
                try:
                    sell_price_call = df_weekly_futures_used[str(new_working_strike) + "C_B"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                    sell_price_put = df_weekly_futures_used[str(new_working_strike) + "P_B"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                    print("YES", sell_price_call,sell_price_put)
                except:
                    new_working_strike = (round(current_future_price / roundoff_factor) * roundoff_factor) + 100
                    sell_price_call = df_weekly_futures_used[str(new_working_strike) + "C_B"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                    sell_price_put = df_weekly_futures_used[str(new_working_strike) + "P_B"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                    print("NO", sell_price_call,sell_price_put)
                    
                # minimum_trade_qty = max(minimum_trade_qty_fix, min(call_qty,put_qty))
                # print(sell_price_call,sell_price_put)
                call_qty = -1*qty_for_next_cycle
                put_qty = -1*qty_for_next_cycle
                # position_active_call = True
                # position_active_put = True
                trade_type_C = 'SELL_StrikeChange_CP'
                trade_type_P = 'SELL_StrikeChange_CP'
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],0,0,sell_price_call,call_qty,0,trade_type_C,
                             put_file_name[:-8],0,0,sell_price_put, put_qty,0,trade_type_P])
                print(date,index_,"Strike change squareoff hit for both options selling end at : ",index_, "new call_qty :", call_qty, "put_qty :", put_qty, 'new_working_strike :',new_working_strike)
                
                
        if((position_active_call == True) & (position_active_put == True) & (delta_neutral_rollover == True)):
            if ((current_future_price<=delta_move_lower_price) | (current_future_price>=delta_move_upper_price)):
                new_call_qty, new_put_qty = cal_call_put_straddle_qty(call_D, put_D, abs(call_qty), abs(put_qty),delta_neutral_rollover)
                call_incr_qty = round(change_qty_trade(new_call_qty,call_qty)[1]*call_qty_delta_neutral_perc/lot_size)*lot_size
                put_incr_qty = round(change_qty_trade(new_put_qty,put_qty)[1]*put_qty_delta_neutral_perc/lot_size)*lot_size
                call_delta_signal=change_qty_trade(new_call_qty,call_qty)[0]
                put_delta_signal=change_qty_trade(new_put_qty,put_qty)[0]
                if call_delta_signal=='BUY':
                    index_c  = index_
                    idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                    buy_price_call = df_weekly_futures_used[str(working_strike) + "C_S"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                    # position_active_call = False
                    print(date,index_,"Delta Neutral for call option buying at : ",df_weekly_futures_used.index[min(idx_c+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_call)
                    trade_type_C = 'BUY_DeltaNeutral_C'
                    # avg_buy_price_call = 
                    # call_qty = call_incr_qty
                    transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                                 strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],buy_price_call,call_incr_qty,0,0,0,trade_type_C,
                                 "",float_nan,float_nan,float_nan, float_nan,float_nan,''])
                    sell_price_call = (sell_price_call * abs(call_qty) - buy_price_call * abs(call_incr_qty))/abs(call_qty+call_incr_qty)
                    call_qty=call_qty+call_incr_qty
                    
                elif call_delta_signal=='SELL':
                    index_c  = index_
                    idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                    prev_sell_value = sell_price_call*call_qty
                    sell_price_call = df_weekly_futures_used[str(working_strike) + "C_B"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                    # position_active_call = False
                    print(date,index_,"Delta Neutral for call option selling at : ",df_weekly_futures_used.index[min(idx_c+1, len(df_weekly_futures_used)-1)], " for : ",sell_price_call)
                    trade_type_C = 'SELL_DeltaNeutral_C'
                    # call_qty = -1*call_incr_qty
                    transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                                 strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],0,0,sell_price_call,-1*call_incr_qty,0,trade_type_C,
                                 "",float_nan,float_nan,float_nan, float_nan,float_nan,''])
                    sell_price_call = (abs(prev_sell_value) + sell_price_call*abs(call_incr_qty))/abs(call_qty-call_incr_qty)
                    call_qty=call_qty-call_incr_qty
                    
                if put_delta_signal == "BUY":
                    index_p  = index_
                    idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                    buy_price_put = df_weekly_futures_used[str(working_strike) + "P_S"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                    # position_active_put = False
                    print(date,index_,"Delta Neutral for  put option buying at : ",df_weekly_futures_used.index[min(idx_p+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_put)
                    trade_type_P = 'BUY_DeltaNeutral_P'
                    # put_qty = 0
                    transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                                 strike_move_upper_price,strike_move_lower_price,'',float_nan,float_nan,float_nan,float_nan,float_nan,'',
                                 put_file_name[:-8],buy_price_put,put_incr_qty,0,0,0,trade_type_P])
                    sell_price_put = (sell_price_put * abs(put_qty) - buy_price_put * abs(put_incr_qty))/abs(put_qty+put_incr_qty)
                    put_qty=put_qty+put_incr_qty
                    
                elif put_delta_signal=='SELL':
                    index_p  = index_
                    idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                    prev_sell_value = sell_price_put*put_qty
                    sell_price_put = df_weekly_futures_used[str(working_strike) + "P_B"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                    # position_active_put = False
                    print(date,index_,"Delta Neutral for  put option buying at : ",df_weekly_futures_used.index[min(idx_p+1, len(df_weekly_futures_used)-1)], " for : ",sell_price_put)
                    trade_type_P = 'SELL_DeltaNeutral_P'
                    # put_qty = 0
                    transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                                 strike_move_upper_price,strike_move_lower_price,'',float_nan,float_nan,float_nan,float_nan,float_nan,'',
                                 put_file_name[:-8],0,0,sell_price_call,-1*put_incr_qty,0,trade_type_P])
                    sell_price_put = (abs(prev_sell_value) + sell_price_put*abs(put_incr_qty))/abs(put_qty-put_incr_qty)
                    put_qty=put_qty-put_incr_qty
                
                delta_move_lower_price=current_future_price*(1-delta_move_fraction)    
                delta_move_upper_price=current_future_price*(1+delta_move_fraction)
                    
        if(position_active_call == True):
            # print(date,index_,"Check Call Position")
            if((check_normal_stoploss == True) & (df_weekly_futures_used[str(working_strike) + "C_S"][index_] >= (1+stoploss_fraction)*sell_price_call)):
                index_c  = index_
                idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                buy_price_call = df_weekly_futures_used[str(working_strike) + "C_S"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                # buy_price_put = df_rel_put_option["C"][df_rel_put_option["C"]["Time"] == df_rel_call_option["Time"][i]]
                position_active_call = False
                max_loss =  max_loss + (sell_price_call-buy_price_call)
                print(date,index_,"Stop loss hit for call bought call option buying at : ",df_weekly_futures_used.index[min(idx_c+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_call , " making profit of : ", (sell_price_call-buy_price_call))
                trade_type_C = 'BUY_Stoploss_C'
                
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],buy_price_call,-1*call_qty,0,0,sell_price_call - buy_price_call,trade_type_C,
                             "",float_nan,float_nan,float_nan, float_nan,float_nan,''])
                
                call_qty = 0
            
            elif((check_combined_stoploss == True) & ((sell_price_call - df_weekly_futures_used[str(working_strike) + "C_S"][index_]) <= -1*max_loss) & (position_active_put == False)):
                index_c  = index_
                idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                buy_price_call = df_weekly_futures_used[str(working_strike) + "C_S"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                position_active_call = False
                print(date,index_,"combine Stop loss hit for call option buying at : ",df_weekly_futures_used.index[min(idx_c+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_call, " making profit of : ", (sell_price_call-buy_price_call))
                trade_type_C = 'BUY_CombinedSL_C'
                # call_qty = 0
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],buy_price_call,-1*call_qty,0,0,sell_price_call - buy_price_call,trade_type_C,
                             "",float_nan,float_nan,float_nan, float_nan,float_nan,''])
                call_qty = 0
                
            elif(index_ == end_time):
                index_c  = index_
                idx_c = np.searchsorted(df_weekly_futures_used.index, index_)
                buy_price_call = df_weekly_futures_used[str(working_strike) + "C_S"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]
                position_active_call = False
                print(date,index_,"Time Close hit for call option buying at : ",df_weekly_futures_used.index[min(idx_c+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_call, " making profit of : ", (sell_price_call-buy_price_call))
                trade_type_C = 'BUY_EndTime_C'
                
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,call_file_name[:-8],buy_price_call,-1*call_qty,0,0,sell_price_call - buy_price_call,trade_type_C,
                             "",float_nan,float_nan,float_nan, float_nan,float_nan,''])
                call_qty = 0
        
        if(position_active_put == True):

            if((check_normal_stoploss == True) & (df_weekly_futures_used[str(working_strike) + "P_S"][index_] >= (1+stoploss_fraction)*sell_price_put)):
                index_p  = index_
                idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                buy_price_put = df_weekly_futures_used[str(working_strike) + "P_S"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                position_active_put = False
                max_loss =  max_loss + (sell_price_put-buy_price_put)
                print(date,index_,"Stop loss hit for put bought put option buying at : ",df_weekly_futures_used.index[min(idx_p+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_put , " making profit of : ", (sell_price_put-buy_price_put) )            
                trade_type_P = 'BUY_Stoploss_P'
                
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,'',float_nan,float_nan,float_nan,float_nan,float_nan,'',
                             put_file_name[:-8],buy_price_put,-1*put_qty,0, 0,sell_price_put-buy_price_put,trade_type_P])
                put_qty = 0
                # continue
            
            elif((check_combined_stoploss == True) & ((sell_price_put - df_weekly_futures_used[str(working_strike) + "P_S"][index_]) <= -1*max_loss) & (position_active_call == False)):
                index_p  = index_
                idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                buy_price_put = df_weekly_futures_used[str(working_strike) + "P_S"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                position_active_put = False
                print(date,index_,"combine Stop loss hit for put option buying at : ",df_weekly_futures_used.index[min(idx_p+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_put , " making profit of : ", (sell_price_put-buy_price_put))
                trade_type_P = 'BUY_CombinedSL_P'
                
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,'',float_nan,float_nan,float_nan,float_nan,float_nan,'',
                             put_file_name[:-8],buy_price_put,-1*put_qty,0, 0,sell_price_put-buy_price_put,trade_type_P])
                put_qty = 0
                # continue
            
            elif(index_ == end_time):
                index_p  = index_
                idx_p = np.searchsorted(df_weekly_futures_used.index, index_)
                buy_price_put = df_weekly_futures_used[str(working_strike) + "P_S"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]
                position_active_put = False
                print(date,index_,"Time close hit for put option buying at : ",df_weekly_futures_used.index[min(idx_p+1, len(df_weekly_futures_used)-1)], " for : ",buy_price_put , " making profit of : ", (sell_price_put-buy_price_put))
                trade_type_P = 'BUY_EndTime_P'
                
                transactions_book.append([date,date_name,index_,current_future_price,delta_move_upper_price,delta_move_lower_price,
                             strike_move_upper_price,strike_move_lower_price,'',float_nan,float_nan,float_nan,float_nan,float_nan,'',
                             put_file_name[:-8],buy_price_put,-1*put_qty,0, 0,sell_price_put-buy_price_put,trade_type_P])
                put_qty = 0

transactions_book_df = pd.DataFrame(transactions_book[1:],   columns = transactions_book[0])
transactions_book_df.to_csv("../res/Output.csv")
#     day_profit[date] = {
#      "day" : pd.to_datetime(date, format = "%d-%m-%Y").strftime("%A"),
#      "Future" : future_price,
#      "ATM Strike" : working_strike,
#      "Sum_Premium_LTP" : df_weekly_futures_used["Call_plus_Put"].loc[start_time], 
#      "Time_start"	: start_time,
#      "Strike to Sell" : working_strike,	
#      "Future at Sell" :future_price,
#      "Call_Sell" : sell_price_call,
#      "Put_Sell" : sell_price_put,	
#      "Sum_Sell" : (sell_price_put +sell_price_call),
     
#      # "Time_SQOFF_Call" : index_c,	
#      # "Future_CALLSQOFF"	: time_temp[wfut_cols[0]][index_c],
#      # "Call Buy"	: buy_price_call,
#      # "Call PNL"	: (sell_price_call-buy_price_call),
     
#      # "Time_SQOFF_Put"	: index_p,	
#      # "Future_PUTSQOFF"	: time_temp[wfut_cols[0]][index_p],
#      # "Put Buy"	: buy_price_put,
#      # "Put PNL"  : (sell_price_put-buy_price_put),
#       "Time_SQOFF_Call" : df_weekly_futures_used.index[min(idx_c+1, len(df_weekly_futures_used)-1)],	
#       "Future_CALLSQOFF"	: df_weekly_futures_used[[str(working_strike)+'WFUT']].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)],
#       "Call Buy"	: df_weekly_futures_used[str(working_strike) + "C_S"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)],
#       "Call PNL"	: (sell_price_call - df_weekly_futures_used[str(working_strike) + "C_S"].iloc[min(idx_c+1, len(df_weekly_futures_used)-1)]),
     
#       "Time_SQOFF_Put"	: df_weekly_futures_used.index[min(idx_p+1, len(df_weekly_futures_used)-1)],	
#       "Future_PUTSQOFF"	: df_weekly_futures_used[[str(working_strike)+'WFUT']].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)],
#       "Put Buy"	: df_weekly_futures_used[str(working_strike) + "P_S"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)],
#       "Put PNL"  : (sell_price_put-df_weekly_futures_used[str(working_strike) + "P_S"].iloc[min(idx_p+1, len(df_weekly_futures_used)-1)]),
     
#      "Time_End"	    : end_time,
#      "Future at end": df_weekly_futures_used[[str(working_strike)+'WFUT']][end_time],
#      "Call_end"	    : df_weekly_futures_used[str(working_strike) + "C_S"].loc[end_time],
#      "Put_end"	    : df_weekly_futures_used[str(working_strike) + "P_S"].loc[end_time],
#      "Sum_end"      : df_weekly_futures_used["Call_plus_Put"].loc[end_time],
     
#      "Time_Max"	    : df_weekly_futures_used["Call_plus_Put"].idxmax(),
#      "Future_Max"	: df_weekly_futures_used[[str(working_strike)+'WFUT']][df_weekly_futures_used["Call_plus_Put"].idxmax()],
#      "Call at Max"	: df_weekly_futures_used[str(working_strike) + "C_S"].loc[df_weekly_futures_used["Call_plus_Put"].idxmax()],
#      "Put at Max"	: df_weekly_futures_used[str(working_strike) + "P_S"].loc[df_weekly_futures_used["Call_plus_Put"].idxmax()],
#      "Sum_Max"      : df_weekly_futures_used["Call_plus_Put"].max(),
     
#      "Time_Min"	    : df_weekly_futures_used["Call_plus_Put"].idxmin(),
#      "Future_Min"	: df_weekly_futures_used[[str(working_strike)+'WFUT']][df_weekly_futures_used["Call_plus_Put"].idxmin()],
#      "Call at Min"	: df_weekly_futures_used[str(working_strike) + "C_S"].loc[df_weekly_futures_used["Call_plus_Put"].idxmin()],
#      "Put at Min"	: df_weekly_futures_used[str(working_strike) + "P_S"].loc[df_weekly_futures_used["Call_plus_Put"].idxmin()],
#      "Sum_Min"      : df_weekly_futures_used["Call_plus_Put"].min(),
#      'Close_Type_Call' : trade_type_C,
#      'Close_Type_Put' : trade_type_P
#          }