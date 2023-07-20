#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 20:08:26 2023

@author: bnsl.j3
"""

# from maticalgos.historical import historical
# import datetime
# ma = historical('bnsl.j3234@gmail.com')
# ma.login(215056)

# use_date = datetime.date(2018,1,1)

# for i in range(1000):
    
#     data = ma.get_data("banknifty", use_date) 
#     use_date = use_date + datetime.timedelta(days=1)
#     # data.set_index("symbol")
#     for symbol in data.symbol.unique():
#         new_df = data[data['symbol']==symbol]
#         new_df.set_index('time', inplace = True)
#         new_df = new_df[['open', 'high', 'low','close' ]]
    
#Data available only for nifty options from 2019 and banknifty options from 2018
#Date should be in datetime.date format
#Data would be in pandas DataFrame format
